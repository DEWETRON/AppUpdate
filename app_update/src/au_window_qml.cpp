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

#include "au_window_qml.h"

#include <QCoreApplication>
#include <QMenu>
#include <QMessageBox>

AuWindowQml::AuWindowQml()
{
    createActions();
    createTrayIcon();

    connect(m_trayIcon, &QSystemTrayIcon::activated, this, &AuWindowQml::iconActivated);

    m_trayIcon->show();

    setTitle(tr("DEWETRON AppUpdate"));
}


bool AuWindowQml::event(QEvent* event)
{
    if (event->type() == QEvent::Close) {
        if (m_trayIcon->isVisible())
        {
            QMessageBox::information(nullptr, tr("DEWETRON AppUpdate"),
                tr("The program will keep running in the "
                    "system tray. To terminate the program, "
                    "choose <b>Quit</b> in the context menu "
                    "of the system tray entry."));
            hide();
            return true;
        }
        else
        {
            return QQuickView::event(event);
        }
    }
    return QQuickView::event(event);
}

void AuWindowQml::iconActivated(QSystemTrayIcon::ActivationReason reason)
{
    switch (reason) {
    case QSystemTrayIcon::Trigger:
    case QSystemTrayIcon::DoubleClick:
        //iconComboBox->setCurrentIndex((iconComboBox->currentIndex() + 1) % iconComboBox->count());
        this->showNormal();
        break;
    case QSystemTrayIcon::MiddleClick:
        //showMessage();
        break;
    default:
        ;
    }
}


void AuWindowQml::showNotification(const QString& title, const QString& body)
{
    m_trayIcon->showMessage(title, body);
}

void AuWindowQml::createActions()
{
    m_minimizeAction = new QAction(tr("Mi&nimize"), this);
    connect(m_minimizeAction, &QAction::triggered, this, &QQuickView::hide);

    m_maximizeAction = new QAction(tr("Ma&ximize"), this);
    connect(m_maximizeAction, &QAction::triggered, this, &QQuickView::showMaximized);

    m_restoreAction = new QAction(tr("&Restore"), this);
    connect(m_restoreAction, &QAction::triggered, this, &QQuickView::showNormal);

    m_quitAction = new QAction(tr("&Quit"), this);
    connect(m_quitAction, &QAction::triggered, qApp, &QCoreApplication::quit);
}


void AuWindowQml::createTrayIcon()
{
    m_trayIconMenu = new QMenu();
    m_trayIconMenu->addAction(m_minimizeAction);
    m_trayIconMenu->addAction(m_maximizeAction);
    m_trayIconMenu->addAction(m_restoreAction);
    m_trayIconMenu->addSeparator();
    m_trayIconMenu->addAction(m_quitAction);

    m_trayIcon = new QSystemTrayIcon(this);
    m_trayIcon->setContextMenu(m_trayIconMenu);

    
    auto icon = QIcon(":/res/dewetron.ico");
    m_trayIcon->setIcon(icon);
    this->setIcon(icon);

    m_trayIcon->setToolTip("DEWETRON AppUpdate");
}
