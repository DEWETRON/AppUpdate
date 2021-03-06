/* 
 * This file is part of the AppUpdate (https://github.com/DEWETRON/AppUpdate)
 * Copyright (c) DEWETRON GmbH 2020.
 * 
 * This program is free software: you can redistribute it and/or modify  
 * it under the terms of the GNU General Public License as published by  
 * the Free Software Foundation, version 3.
 *
 * This program is distributed in the hope that it will be useful, but 
 * WITHOUT ANY WARRANTY; without even the implied warranty of 
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License 
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 */

#include "au_application_data.h"
#include "au_update_json.h"
#include "au_version_number.h"
#include <QCoreApplication>
#include <QCryptographicHash>
#include <QDesktopServices>
#include <QDir>
#include <QFile>
#include <QStandardPaths>


#define UPDATE_PORTAL "https://ccc.dewetron.com/dl/update.json"
#define UPDATE_FILE   "update.json"


bool getAutostartSetting();
void setAutostartSetting(bool autostart);


AuApplicationData::AuApplicationData()
    : m_installed_software{}
    , m_installed_software_internal{}
    , m_sw_enumerator()
    , m_bundle_map()
    , m_au_doc()
    , m_downloads()
    , m_message()
    , m_progress()
    , m_filename_map()
    , m_daily_timer()
    , m_fast_timer()
    , m_autostart(false)
    , m_show_beta_versions(false)
    , m_show_older_versions(false)
{
    // predefine bundles, which are only shown once
    m_bundle_map = std::map<std::string, std::string>
    {
        { "DEWETRON TRION Driver", "DEWETRON TRION Applications" },
        { "DEWETRON DEWE2 Driver", "DEWETRON TRION Applications" },
        { "DEWETRON Explorer",     "DEWETRON TRION Applications" },
        { "DEWETRON TRIONCAL",     "DEWETRON TRION Applications" }
    };

    m_daily_timer = new QTimer(this);
    connect(m_daily_timer, &QTimer::timeout, this, QOverload<>::of(&AuApplicationData::update));
    m_daily_timer->start(1000 * 60 * 60 * 24);   // check every 24hours

    m_autostart = getAutostartSetting();

    update();
}

AuApplicationData::~AuApplicationData()
{
    if (m_daily_timer)
    {
        delete m_daily_timer;
    }

    if (m_fast_timer)
    {
        delete m_fast_timer;
    }
}

QVariantList AuApplicationData::getInstalledSoftware()
{
    return m_installed_software;
}

QVariantList AuApplicationData::getInstalledApps()
{
    QVariantList apps;
    for (auto app : m_installed_software_internal) {
        
        QVariantMap entry;
        entry["name"] = app.package_name.c_str();
        entry["version"] = app.package_version.c_str();
        apps.push_back(entry);
    }
    return apps;
}

QVariantList AuApplicationData::getUpdateableApps()
{
    QVariantList apps;
    for (auto app : m_au_doc.m_apps) {

        QVariantMap entry;
        entry["name"] = app.first.c_str();
        auto sorted_vn = getSortedVersionNumbers(app.first);

        if (sorted_vn.isEmpty()) continue;

        // Highest version first
        {
            auto ver = sorted_vn.first();
            sorted_vn.pop_front();
            auto app_version = app.second.m_app_versions[ver.toString().toStdString().c_str()];

            entry["beta"] = app_version.beta.c_str();
            entry["version"] = app_version.version.c_str();
            entry["release_date"] = app_version.release_date.c_str();
            entry["license"] = app_version.license.c_str();
            entry["url"] = app_version.url.c_str();
            entry["is_older_version"] = false;
            entry["notify"] = app_version.notify.c_str();

            QString changes("Changes:\n");
            for (auto change : app_version.changes) {
                changes += "- " + QString(change.c_str()) + "\n";
            }

            // update available?
            bool has_update = false;
            has_update = hasUpdate(app.first, ver.toString().toStdString());
            
            entry["has_update"] = has_update;
            entry["changes"] = changes;
        }

        
        apps.push_back(entry);
       
        // look at older mentioned versions -> stored in entry.other map

        for (auto ver : sorted_vn)
        {
            auto app_version = app.second.m_app_versions[ver.toString().toStdString().c_str()];
            
            QVariantMap other_entry;

            other_entry["name"] = app.first.c_str();
            other_entry["beta"] = app_version.beta.c_str();
            other_entry["release_date"] = app_version.release_date.c_str();
            other_entry["version"] = app_version.version.c_str();
            other_entry["license"] = app_version.license.c_str();
            other_entry["url"] = app_version.url.c_str();
            other_entry["is_older_version"] = true;
            other_entry["notify"] = app_version.notify.c_str();

            QString changes("Changes:\n");
            for (auto change : app_version.changes) {
                changes += "- " + QString(change.c_str()) + "\n";
            }

            other_entry["changes"] = changes;
            apps.push_back(other_entry);
        }
    }

    auto filtered_updates = optionFilter(apps);

    for (const auto upd : filtered_updates)
    {
        QVariantMap entry = qvariant_cast<QVariantMap>(upd);
        auto has_update = entry["has_update"].toBool();
        auto notify = entry["notify"].toString();
        auto name = entry["name"].toString();
        auto version = entry["version"].toString();
        
        if (has_update && (notify != "false"))
        {
            showNotification(name, QString(tr("New update %1 available")).arg(version));
        }

    }

    return filtered_updates;
}


QString AuApplicationData::getMessage() const
{
    return m_message;
}

void AuApplicationData::setMessage(QString message)
{
    m_message = message;
    Q_EMIT messageChanged();
}

QVariantList AuApplicationData::optionFilter(const QVariantList& apps)
{
    bool show_update_only = (!m_show_beta_versions && !m_show_older_versions);

    QVariantList filtered_apps(apps);

    // Filter out invalid entries
    auto it = filtered_apps.begin();
    while (it != filtered_apps.end())
    {
        QVariantMap entry = qvariant_cast<QVariantMap>(*it);

        {
            if (!m_show_beta_versions)
            {
                if (entry["beta"].toString() == "1")
                {
                    it = filtered_apps.erase(it);
                    continue;
                }
            }

            if (!m_show_older_versions)
            {
                if (entry["is_older_version"].toBool())
                {
                    it = filtered_apps.erase(it);
                    continue;
                }
            }
        }
        it++;
    }

    {
        auto it = filtered_apps.begin();
        while (it != filtered_apps.end())
        {
            QVariantMap entry = qvariant_cast<QVariantMap>(*it);

            if (show_update_only)
            {
                if (!entry["has_update"].toBool())
                {
                    it = filtered_apps.erase(it);
                    continue;
                }
            }
            it++;
        }
    }

    return filtered_apps;
}

bool AuApplicationData::getAutostart() const
{
    return m_autostart;
}

void AuApplicationData::setAutostart(bool autostart_enable)
{
#ifdef Q_OS_WIN
    m_autostart = autostart_enable;
    setAutostartSetting(m_autostart);
#else
    // TODO other OS
#endif
    Q_EMIT autostartChanged();
}

void AuApplicationData::checkForUpdates()
{
    update();
}

void AuApplicationData::updateAll()
{
    // TODO:
    // check for updates
    // download updates
    // install
}

void AuApplicationData::download(QUrl download_url)
{
    doDownload(download_url, {});
}

int AuApplicationData::getDownloadProgress(QUrl download_url)
{
    return m_progress[download_url];
}

void AuApplicationData::openDownloadFolder(QUrl download_url)
{
    QString file_name;
    auto file_name_it = m_filename_map.find(download_url);
    if (file_name_it != m_filename_map.end())
    {
        file_name = file_name_it.value();
    }

    const QString downloads_folder = QStandardPaths::writableLocation(QStandardPaths::DownloadLocation);
    if (!QDesktopServices::openUrl(QUrl(downloads_folder + "/" + file_name, QUrl::TolerantMode)))
    {
        QDesktopServices::openUrl(QUrl(downloads_folder, QUrl::TolerantMode));
    }

    if (!m_fast_timer)
    {
        m_fast_timer = new QTimer(this);
        connect(m_fast_timer, &QTimer::timeout, this, QOverload<>::of(&AuApplicationData::update));
        m_fast_timer->setSingleShot(true);
        m_fast_timer->start(1000 * 60);   // check after a minute
    }
}

void AuApplicationData::showNotification(const QString& title, const QString& body)
{
    Q_EMIT doShowNotification(title, body);
}

void AuApplicationData::update()
{
    Q_EMIT resetAlertIcon();

    if (m_fast_timer)
    {
        m_fast_timer->stop();
        delete m_fast_timer;
        m_fast_timer = nullptr;
    }
    // download latest update.json file from server
    doDownload(QUrl(UPDATE_PORTAL), UPDATE_FILE);
}


std::string AuApplicationData::getBundleName(const std::string& sw_display_name) const
{
    auto it = m_bundle_map.find(sw_display_name);
    if (it != m_bundle_map.end())
    {
        return it->second;
    }
    return {};
}

void AuApplicationData::addToSwList(const SwEntry& sw_entry, const AuVersionNumber& latest_version)
{
    auto bundle_name = getBundleName(sw_entry.m_sw_display_name);
    std::string app_name = bundle_name.empty() ? sw_entry.m_sw_display_name : bundle_name;

    if (std::none_of(m_installed_software_internal.begin(), m_installed_software_internal.end(),
        [app_name](SwComponent sw_entry) {
            return sw_entry.package_name == app_name;
        }))
    {
        SwComponent one_entry{ app_name.c_str(),
            sw_entry.m_sw_version.c_str(),
            sw_entry.m_publisher.c_str(),
            latest_version.toString().toStdString()
        };

        m_installed_software_internal.push_back(one_entry);
    }
}

QVariantList AuApplicationData::toVariantList(const std::vector<SwComponent>& sw_list)
{
    QVariantList v_list;

    for (const auto& sw_entry : sw_list)
    {
        QVariantList entry;
        entry.push_back(sw_entry.package_name.c_str());
        entry.push_back(sw_entry.package_version.c_str());
        entry.push_back(sw_entry.latest_package_version.c_str());

        v_list.push_back(entry);
    }

    return v_list;
}

AuVersionNumber AuApplicationData::getHighestVersionNumber(const SwEntry& sw_entry)
{
    AuVersionNumber highest_version;

    auto bundle_name = getBundleName(sw_entry.m_sw_display_name);
    std::string app_name = bundle_name.empty() ? sw_entry.m_sw_display_name : bundle_name;

    auto it = m_au_doc.m_apps.find(app_name);
    if (it != m_au_doc.m_apps.end())
    {
        auto avail_versions = it->second.m_app_versions;
        for (auto version_it = avail_versions.begin(); version_it != avail_versions.end(); version_it++)
        {
            auto qver = AuVersionNumber::fromString(version_it->first.c_str());
            if (qver > highest_version) highest_version = qver;
        }
    }

    auto debug = highest_version.toString();

    return highest_version;
}

QList<AuVersionNumber> AuApplicationData::getSortedVersionNumbers(const std::string& app_name) const
{
    QList<AuVersionNumber> sorted_version_numbers;

    auto it = m_au_doc.m_apps.find(app_name);
    if (it != m_au_doc.m_apps.end())
    {
        auto avail_versions = it->second.m_app_versions;
        for (auto version_it = avail_versions.begin(); version_it != avail_versions.end(); version_it++)
        {
            auto curr_ver = AuVersionNumber::fromString(version_it->first.c_str());
            bool inserted = false;
            for (auto it = sorted_version_numbers.begin(); it != sorted_version_numbers.end(); ++it)
            {
                if (curr_ver > *it)
                {
                    sorted_version_numbers.insert(it, curr_ver);
                    inserted = true;
                    break;
                }
            }
            if (!inserted)
            {
                sorted_version_numbers.push_back(curr_ver);
            }
        }
    }
    return sorted_version_numbers;
}

void AuApplicationData::updateBundleMap()
{
    std::map<std::string, std::string> bundle_map;

    for (auto app : m_au_doc.m_apps)
    {
        for (auto ver : app.second.m_app_versions)
        {
            for (auto part_of_bundle : ver.second.bundle)
            {
                bundle_map.insert({ part_of_bundle, app.first});
            }
        }
    }

    // replace old map
    m_bundle_map = bundle_map;
}

bool AuApplicationData::hasUpdate(const std::string& app_name, const std::string& upd_ver) const
{
    auto installed_app = std::find_if(m_installed_software_internal.begin(),
        m_installed_software_internal.end(),
        [app_name](const SwComponent& sw) {
            return sw.package_name == app_name;
    });

    if (installed_app != m_installed_software_internal.end())
    {
        auto upd_version = AuVersionNumber::fromString(upd_ver.c_str());
        auto inst_version = AuVersionNumber::fromString(installed_app->package_version.c_str());
        auto ret = upd_version > inst_version;
        return ret;
    }

    // Not installed -> update true by default
    return true;
}

bool AuApplicationData::doDownload(QUrl download_url, const QString nice_name)
{
    auto dl_it = m_downloads.find(download_url);

    if (dl_it != m_downloads.end())
    {
        // download in progress - ignore
        return false;
    }

    setMessage(QString("Downloading %1").arg(nice_name));

    auto au_dl = new AuDownloader(download_url, this);
    m_downloads.insert(download_url, au_dl );

    connect(au_dl, &AuDownloader::downloadFinished, this, &AuApplicationData::downloadFinished);
    connect(au_dl, &AuDownloader::downloadError, this, &AuApplicationData::downloadError);
    connect(au_dl, &AuDownloader::downloadProgress, this, &AuApplicationData::downloadProgress);

    return true;
}

void AuApplicationData::downloadFinished(QUrl dl_url, QString filename)
{
    setMessage({});

    auto au_dl_it = m_downloads.find(dl_url);
    if (au_dl_it != m_downloads.end())
    {
        auto au_dl = au_dl_it.value();
        disconnect(au_dl, &AuDownloader::downloadFinished, this, &AuApplicationData::downloadFinished);
        disconnect(au_dl, &AuDownloader::downloadError, this, &AuApplicationData::downloadError);
        disconnect(au_dl, &AuDownloader::downloadProgress, this, &AuApplicationData::downloadProgress);
    }

    auto content = au_dl_it.value()->getDownload();


    if ((QUrl(UPDATE_PORTAL) == dl_url) && (filename == UPDATE_FILE))
    {
        m_downloads.erase(au_dl_it);
        updateJson(content);
        return;
    }

    // Check signatures
    {
        QCryptographicHash md5(QCryptographicHash::Md5);
        md5.addData(content);
        if (!compareHashMd5(dl_url, md5.result()))
        {
            setMessage(QString("MD5 checksum failure for file %1").arg(filename));
            return;
        }
    }

    {
        QCryptographicHash sha1(QCryptographicHash::Sha1);
        sha1.addData(content);
        if (!compareHashSha1(dl_url, sha1.result()))
        {
            setMessage(QString("SHA1 checksum failure for file %1").arg(filename));
            return;
        }
    }

    m_filename_map[dl_url] = filename;

    const QString downloads_folder = QStandardPaths::writableLocation(QStandardPaths::DownloadLocation);
    QFile dest_file(downloads_folder + "/" + filename);

    if (dest_file.exists())
    {
        // removing old file
        dest_file.remove();
    }

    if (!dest_file.open(QIODevice::WriteOnly))
    {
        setMessage(QString("Could not create ") + dest_file.fileName());
    }
    auto bytes_written = dest_file.write(content);
    dest_file.close();
    setMessage(QString("File downloaded to ") + dest_file.fileName());
    

    m_progress[dl_url] = 200;  // signal finished dl
    Q_EMIT downloadProgressChanged();

    m_downloads.erase(au_dl_it);
}

void AuApplicationData::downloadError(QUrl dl_url)
{
    auto au_dl_it = m_downloads.find(dl_url);
    if (au_dl_it != m_downloads.end())
    {
        auto au_dl = au_dl_it.value();
        disconnect(au_dl, &AuDownloader::downloadFinished, this, &AuApplicationData::downloadFinished);
        disconnect(au_dl, &AuDownloader::downloadError, this, &AuApplicationData::downloadError);
        disconnect(au_dl, &AuDownloader::downloadProgress, this, &AuApplicationData::downloadProgress);

        setMessage(QString("Download error: %1").arg(au_dl->getError()));
    }

    if ((QUrl(UPDATE_PORTAL) == dl_url))
    {
        QStringList update_candidates{ "examples/update.json", "../examples/update.json" };
        QByteArray json_data;
        for (const auto& candidate : update_candidates)
        {
            QFile uf(candidate);
            if (uf.open(QIODevice::ReadOnly))
            {
                json_data = uf.readAll();
                updateJson(json_data);
                break;
            }
        }
    }

    m_downloads.erase(au_dl_it);
}

void AuApplicationData::downloadProgress(QUrl dl_url, qint64 curr, qint64 max)
{
    auto progress = (100.0 / max) * curr;
    
    m_progress[dl_url] = progress; 
    Q_EMIT downloadProgressChanged();
}

void AuApplicationData::updateJson(const QByteArray& json)
{
    // get update json document
    AuUpdateJson au_json(json);

    if (au_json.update())
    {
        m_au_doc = au_json.getDocument();
        updateBundleMap();
    }

    // add a custom filter to display only relevant software packages
    m_sw_enumerator.addFilter([](const SwEntry& sw) { return sw.m_publisher.find("DEWETRON") != std::string::npos; });

    auto sw_entries = m_sw_enumerator.enumerate();

    m_installed_software_internal.clear();

    // create list of installed sw
    for (const auto& sw_entry : sw_entries)
    {
       AuVersionNumber latest_version(getHighestVersionNumber(sw_entry));
       addToSwList(sw_entry, latest_version);
    }

    m_installed_software = toVariantList(m_installed_software_internal);

    Q_EMIT updateableAppsChanged();
}

bool AuApplicationData::compareHashMd5(QUrl download_url, const QByteArray& checksum) const
{
    for (auto app : m_au_doc.m_apps) {

        auto sorted_vn = getSortedVersionNumbers(app.first);

        if (sorted_vn.isEmpty()) continue;

        // Highest version first
        {
            auto ver = sorted_vn.first();
            sorted_vn.pop_front();
            auto app_version = app.second.m_app_versions[ver.toString().toStdString().c_str()];

            if (app_version.url == download_url.toString().toStdString())
            {
                return app_version.md5 == checksum.toHex().toStdString();
            }
        }
        // look at older mentioned versions -> stored in entry.other map
        for (auto ver : sorted_vn)
        {
            auto app_version = app.second.m_app_versions[ver.toString().toStdString().c_str()];

            if (app_version.url == download_url.toString().toStdString())
            {
                return app_version.md5 == checksum.toStdString();
            }
        }
    }

    return false;
}

bool AuApplicationData::compareHashSha1(QUrl download_url, const QByteArray& checksum) const
{
    for (auto app : m_au_doc.m_apps) {

        auto sorted_vn = getSortedVersionNumbers(app.first);

        if (sorted_vn.isEmpty()) continue;

        // Highest version first
        {
            auto ver = sorted_vn.first();
            sorted_vn.pop_front();
            auto app_version = app.second.m_app_versions[ver.toString().toStdString().c_str()];

            if (app_version.url == download_url.toString().toStdString())
            {
                return app_version.sha1 == checksum.toHex().toStdString();
            }
        }
        // look at older mentioned versions -> stored in entry.other map
        for (auto ver : sorted_vn)
        {
            auto app_version = app.second.m_app_versions[ver.toString().toStdString().c_str()];

            if (app_version.url == download_url.toString().toStdString())
            {
                return app_version.sha1 == checksum.toStdString();
            }
        }
    }

    return false;
}

bool AuApplicationData::getShowBetaVersion() const
{
    return m_show_beta_versions;
}

void AuApplicationData::setShowBetaVersion(bool beta_version)
{
    m_show_beta_versions = beta_version;
    Q_EMIT showBetaVersionsChanged();
    Q_EMIT updateableAppsChanged();
}

bool AuApplicationData::getShowOlderVersion() const
{
    return m_show_older_versions;
}

void AuApplicationData::setShowOlderVersion(bool older_version)
{
    m_show_older_versions = older_version;
    Q_EMIT showOlderVersionsChanged();
    Q_EMIT updateableAppsChanged();
}


#ifdef Q_OS_WIN

#include "windows.h"

bool getAutostartSetting()
{
    HKEY hrun = NULL;
    DWORD dwType = KEY_ALL_ACCESS;
    char app_path[1024] = { 0 };
    DWORD app_path_size = sizeof(app_path);
    const char* root = "Software\\Microsoft\\Windows\\CurrentVersion\\Run";
    bool autostart_enabled = false;

    if (RegOpenKeyEx(HKEY_CURRENT_USER, root, 0, KEY_READ, &hrun) != ERROR_SUCCESS)
    {
        return autostart_enabled;
    }
   
    if (RegQueryValueEx(hrun, "DEWETRON AppUpdate", NULL, 
            &dwType, (unsigned char*)app_path, &app_path_size) == ERROR_SUCCESS)
    {
        autostart_enabled = true;
    }

    RegCloseKey(hrun);

    return autostart_enabled;
}

void setAutostartSetting(bool autostart)
{
    HKEY hrun = NULL;
    DWORD dwType = KEY_ALL_ACCESS;
    char app_path[1024] = { 0 };
    DWORD app_path_size = sizeof(app_path);
    const char* root = "Software\\Microsoft\\Windows\\CurrentVersion\\Run";
    //bool autostart_enabled = false;

    if (RegOpenKeyEx(HKEY_CURRENT_USER, root, 0, KEY_ALL_ACCESS, &hrun) != ERROR_SUCCESS)
    {
        return;
    }

    if (!autostart)
    {
        RegDeleteValue(hrun, "DEWETRON AppUpdate");
        RegDeleteKey(hrun, "DEWETRON AppUpdate");
    }
    else
    {

        QString app_path = "\"" + QDir::toNativeSeparators(QCoreApplication::applicationFilePath()) + "\"";
        if (RegSetValueEx(hrun, "DEWETRON AppUpdate", 0, REG_SZ, (unsigned char*)app_path.toStdString().data(), (DWORD)app_path.toStdString().size()) != ERROR_SUCCESS)
        {
            RegCloseKey(hrun);
            return;
        }
    }

    RegCloseKey(hrun);
}
#endif

#ifdef Q_OS_UNIX
bool getAutostartSetting()
{
    return false;
}
void setAutostartSetting(bool autostart)
{

}
#endif


