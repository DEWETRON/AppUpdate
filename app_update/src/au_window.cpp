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

#include "au_window.h"

#ifndef QT_NO_SYSTEMTRAYICON

#ifdef WIN32
#include "au_registry_win.h"
#endif

#include <QCloseEvent>
#include <QCoreApplication>
#include <QGridLayout>
#include <QHeaderView>
#include <QLabel>
#include <QMenu>
#include <QMessageBox>
#include <QTableWidget>


AuWindow::AuWindow()
    : QDialog(nullptr, Qt::WindowSystemMenuHint | Qt::WindowTitleHint | Qt::WindowMinMaxButtonsHint | Qt::WindowCloseButtonHint)
 {
    createActions();
    createTrayIcon();

    connect(m_trayIcon, &QSystemTrayIcon::activated, this, &AuWindow::iconActivated);

    auto mainLayout = new QGridLayout;

#ifdef WIN32
    auto sw_registry = AuRegistry();
    sw_registry.enumInstalledSoftware();
    auto dewetron_sw = sw_registry.getInstalledSw();


    auto sw_table = new QTableWidget(dewetron_sw.size(), 3, this);

    sw_table->setHorizontalHeaderLabels({"Name", "Version", "Latest Release"});
    sw_table->horizontalHeader()->setSectionResizeMode(0, QHeaderView::Stretch);
    sw_table->verticalHeader()->setVisible(false);
    sw_table->setAlternatingRowColors(true);

    for (auto i = 0; i<dewetron_sw.size(); ++i)
    {
        const auto& dw_sw = dewetron_sw.at(i);

        {
            QTableWidgetItem* newItem = new QTableWidgetItem(dw_sw.m_sw_display_name.c_str());
            sw_table->setItem(i, 0, newItem);
        }
        {
            QTableWidgetItem* newItem = new QTableWidgetItem(dw_sw.m_sw_version.c_str());
            sw_table->setItem(i, 1, newItem);

        }
    }

    mainLayout->addWidget(sw_table);
#endif

    setLayout(mainLayout);

    m_trayIcon->show();

    setWindowTitle(tr("DEWETRON AppUpdate"));
    resize(500, 300);
}

void AuWindow::setVisible(bool visible)
{
    m_minimizeAction->setEnabled(visible);
    m_maximizeAction->setEnabled(!isMaximized());
    m_restoreAction->setEnabled(isMaximized() || !visible);
    QDialog::setVisible(visible);
}

void AuWindow::closeEvent(QCloseEvent* event)
{
#ifdef Q_OS_MACOS
    if (!event->spontaneous() || !isVisible()) {
        return;
    }
#endif
    if (m_trayIcon->isVisible()) {
        QMessageBox::information(this, tr("Systray"),
            tr("The program will keep running in the "
                "system tray. To terminate the program, "
                "choose <b>Quit</b> in the context menu "
                "of the system tray entry."));
        hide();
        event->ignore();
    }
}

void AuWindow::iconActivated(QSystemTrayIcon::ActivationReason reason)
{
    switch (reason) {
    case QSystemTrayIcon::Trigger:
    case QSystemTrayIcon::DoubleClick:
        //iconComboBox->setCurrentIndex((iconComboBox->currentIndex() + 1) % iconComboBox->count());
        this->showNormal();
        break;
    case QSystemTrayIcon::MiddleClick:
        showMessage();
        break;
    default:
        ;
    }
}


void AuWindow::showMessage()
{

}


void AuWindow::createActions()
{
    m_minimizeAction = new QAction(tr("Mi&nimize"), this);
    connect(m_minimizeAction, &QAction::triggered, this, &QWidget::hide);

    m_maximizeAction = new QAction(tr("Ma&ximize"), this);
    connect(m_maximizeAction, &QAction::triggered, this, &QWidget::showMaximized);

    m_restoreAction = new QAction(tr("&Restore"), this);
    connect(m_restoreAction, &QAction::triggered, this, &QWidget::showNormal);

    m_quitAction = new QAction(tr("&Quit"), this);
    connect(m_quitAction, &QAction::triggered, qApp, &QCoreApplication::quit);
}

void AuWindow::createTrayIcon()
{
    m_trayIconMenu = new QMenu(this);
    m_trayIconMenu->addAction(m_minimizeAction);
    m_trayIconMenu->addAction(m_maximizeAction);
    m_trayIconMenu->addAction(m_restoreAction);
    m_trayIconMenu->addSeparator();
    m_trayIconMenu->addAction(m_quitAction);

    m_trayIcon = new QSystemTrayIcon(this);
    m_trayIcon->setContextMenu(m_trayIconMenu);

    auto icon = QIcon(":/dewetron.ico");
    m_trayIcon->setIcon(icon);
    setWindowIcon(icon);

    m_trayIcon->setToolTip("DEWETRON AppUpdate");
}

#endif
