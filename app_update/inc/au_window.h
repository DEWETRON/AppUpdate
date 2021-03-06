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

#include <QSystemTrayIcon>
#include <QDialog>


class AuWindow : public QDialog
{
    Q_OBJECT
public:
    AuWindow();

    void setVisible(bool visible) override;

protected:
    void closeEvent(QCloseEvent* event) override;

private Q_SLOTS:
    void iconActivated(QSystemTrayIcon::ActivationReason reason);
    void showMessage();

private:
    void createActions();
    void createTrayIcon();

private:
    QAction* m_minimizeAction;
    QAction* m_maximizeAction;
    QAction* m_restoreAction;
    QAction* m_quitAction;

    QSystemTrayIcon* m_trayIcon;
    QMenu* m_trayIconMenu;
};
