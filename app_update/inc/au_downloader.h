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

#include <QObject>
#include <QByteArray>
#include <QList>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QUrl>

class AuDownloader: public QObject
{
    Q_OBJECT

public:
    AuDownloader(QUrl dl_url, QObject* parent = nullptr);
    ~AuDownloader();

    const QByteArray& getDownload() const;
    QUrl getUrl() const;
    QString getError() const;

Q_SIGNALS:
    void downloadFinished(QUrl, QString filename);
    void downloadError(QUrl);
    void downloadProgress(QUrl, qint64 curr, qint64 max);

private:
    Q_SLOT void fileDownloaded(QNetworkReply* reply);
    Q_SLOT void dlProgress(qint64 ist, qint64 max);
    Q_SLOT void sslErrors(const QList<QSslError>& ssl_errors);

private:
    QUrl m_dl_url;
    QNetworkAccessManager m_net_access;
    QByteArray m_downloaded_data;
    QNetworkReply::NetworkError m_error;
    QList<QSslError> m_ssl_errors;
};
