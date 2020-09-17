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

#include "au_downloader.h"
#include <QNetworkRequest>
#include <QMetaEnum>

AuDownloader::AuDownloader(QUrl dl_url, QObject* parent)
    : QObject(parent)
    , m_dl_url(dl_url)
    , m_net_access()
    , m_downloaded_data()
    , m_error()
{
    connect(&m_net_access, &QNetworkAccessManager::finished, this, &AuDownloader::fileDownloaded);

    QNetworkRequest request(m_dl_url);
    auto reply = m_net_access.get(request);
    connect(reply, &QNetworkReply::downloadProgress, this, &AuDownloader::dlProgress);
}

AuDownloader::~AuDownloader()
{

}

void AuDownloader::fileDownloaded(QNetworkReply* reply)
{
    m_error = reply->error();
    if (m_error == QNetworkReply::NoError)
    {
        // Content-Disposition --- "attachment; filename=\"DEWETRON_Oxygen_Setup_R5.2.0_x64.zip\""
        auto content_disp = reply->header(QNetworkRequest::KnownHeaders::ContentDispositionHeader).toString();
        QString filename = content_disp.remove("attachment; filename=");
        filename.remove('\"');
        m_downloaded_data = reply->readAll();
        reply->deleteLater();
        Q_EMIT downloadFinished(m_dl_url, filename);
    }
    else
    {
        auto err_str = QVariant::fromValue(m_error).toString();
        Q_EMIT downloadError(m_dl_url);
    }
}

void AuDownloader::dlProgress(qint64 curr, qint64 max)
{
    Q_EMIT downloadProgress(m_dl_url, curr, max);
}


const QByteArray& AuDownloader::getDownload() const
{
    return m_downloaded_data;
}

QUrl AuDownloader::getUrl() const
{
    return m_dl_url;
}

QNetworkReply::NetworkError AuDownloader::getError() const
{
    return m_error;
}
