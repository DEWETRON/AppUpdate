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

#pragma once

#include "au_downloader.h"
#include "au_software_enumerator.h"
#include "au_update_json.h"

#include <map>
#include <QObject>
#include <QStringList>
#include <QTimer>
#include <QVariant>

class QVersionNumber;

struct SwComponent
{
    std::string package_name;
    std::string package_version;
    std::string publisher;
    std::string latest_package_version;
};


 /**
  * Application main model
  */
class AuApplicationData : public QObject
{
    Q_OBJECT

    Q_PROPERTY(QVariantList installedSoftware
                READ getInstalledSoftware
                NOTIFY installedSoftwareChanged)

    Q_PROPERTY(QVariantList installedApps
                READ getInstalledApps
                NOTIFY installedAppsChanged)

    Q_PROPERTY(QVariantList updateableApps
                READ getUpdateableApps
                NOTIFY updateableAppsChanged)

    Q_PROPERTY(QString message
                READ getMessage
                NOTIFY messageChanged)

    //Q_PROPERTY(int downloadProgress
    //            READ getDownloadProgress
    //            NOTIFY downloadProgressChanged)


public:
    AuApplicationData();
    ~AuApplicationData();

    QVariantList getInstalledSoftware();
    QVariantList getInstalledApps();
    QVariantList getUpdateableApps();
    QString getMessage() const;
    void setMessage(QString message);

    Q_INVOKABLE void checkForUpdates();
    Q_INVOKABLE void updateAll();
    Q_INVOKABLE void download(QUrl download_url);
    Q_INVOKABLE int getDownloadProgress(QUrl download_url);
    Q_INVOKABLE void openDownloadFolder(QUrl download_url);
Q_SIGNALS:
    void installedSoftwareChanged();
    void installedAppsChanged();
    void updateableAppsChanged();
    void messageChanged();
    void downloadProgressChanged();

private:
    Q_SLOT void downloadFinished(QUrl dl_url, QString filename);
    Q_SLOT void downloadError(QUrl dl_url);
    Q_SLOT void downloadProgress(QUrl dl_url, qint64 curr, qint64 max);

private:
    void update();
    std::string getBundleName(const std::string& sw_display_name) const;
    void addToSwList(const SwEntry& sw_entry, const QVersionNumber& latest_version);
    QVariantList toVariantList(const std::vector<SwComponent>& sw_list);
    QVersionNumber getHighestVersionNumber(const SwEntry& sw_entry);
    QList<QVersionNumber> getSortedVersionNumbers(const std::string& app_name) const;
    void updateBundleMap();
    bool hasUpdate(const std::string& app_name, const std::string& upd_ver) const;
    bool doDownload(QUrl download_url, const QString nice_name);
    void updateJson(const QByteArray& json);

    bool compareHashMd5(QUrl download_url, const QByteArray& checksum) const;
    bool compareHashSha1(QUrl download_url, const QByteArray& checksum) const;

private:
    QVariantList m_installed_software;
    std::vector<SwComponent> m_installed_software_internal;
    AuSoftwareEnumerator m_sw_enumerator;
    std::map<std::string, std::string> m_bundle_map;
    au_doc::AuDoc m_au_doc;
    QMap<QUrl, AuDownloader*> m_downloads;
    QString m_message;
    QMap<QUrl, int> m_progress;
    QMap<QUrl, QString> m_filename_map;
    QTimer* m_daily_timer;
    QTimer* m_fast_timer;
};

