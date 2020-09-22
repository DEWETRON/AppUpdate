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

#include <QString>
#include <QLockFile>


/**
 * @brief Help determine that only a single instance of the application is running on this system.
 *
 * In order to accomplish this, a system-wide lock file is used. Call isFirstInstance() to check if
 * this object is the first one to try to acquire the lock.
 */
class AuSingleInstance
{
public:
    explicit AuSingleInstance(const QString& id);
    ~AuSingleInstance();
    bool isFirstInstance() const;

private:
    QString m_id;
    QLockFile* m_lock_file;
};
