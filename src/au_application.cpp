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

#include "au_application.h"
#include "au_window_qml.h"

#include <QFileInfo>
#include <QQmlEngine>

AuApplication::AuApplication(int& argc, char** argv)
    : QObject(nullptr)
    , m_app(argc, argv)
    , m_app_data(nullptr)
    , m_main_window(nullptr)
    , m_qml_main_file()
    , m_qml_reloader(nullptr)
{
}

AuApplication::~AuApplication()
{
    delete m_qml_reloader;
}

bool AuApplication::init()
{
    // Setup main.qml
    m_qml_main_file = "../qml/main.qml";
    QFileInfo qml_file_info(m_qml_main_file);
    auto qml_path = qml_file_info.absolutePath();

    // Handle dynamic qml changes
    m_qml_reloader = new QmlReloader;
    m_qml_reloader->addDirectoryToWatch(qml_path, QStringList() << "*.qml" << "*.js", true);
  

    if (!initGui()) return false;

    return true;
}

bool AuApplication::initGui()
{
    m_main_window = new AuWindowQml;
    m_main_window->connect(m_main_window->engine(), &QQmlEngine::quit, &m_app, &QCoreApplication::quit);
    //m_main_window->setSource(QUrl("qrc:/main.qml"));
    //m_main_window->setSource(QUrl("qml/main.qml"));
    m_main_window->setSource(QUrl(m_qml_main_file));

    if (m_main_window->status() == QQuickView::Error)
        return false;

    m_main_window->setResizeMode(QQuickView::SizeRootObjectToView);
    m_main_window->show();
    m_qml_reloader->addView(m_main_window);

    return true;
}

int AuApplication::run()
{
    int ret = 0;

    ret = m_app.exec();

    return ret;
}

