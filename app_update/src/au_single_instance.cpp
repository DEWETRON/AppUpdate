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

#include "au_single_instance.h"
#include <QStandardPaths>

AuSingleInstance::AuSingleInstance(const QString& id)
    : m_id(id)
    , m_lock_file()
{
    const QString temp_folder = QStandardPaths::writableLocation(QStandardPaths::TempLocation);

    m_lock_file = new QLockFile(temp_folder + "/" + m_id);

    m_lock_file->tryLock();
}

AuSingleInstance::~AuSingleInstance()
{
    if (m_lock_file->isLocked())
    {
        m_lock_file->unlock();
    }
    delete m_lock_file;
}


bool AuSingleInstance::isFirstInstance() const
{
    return m_lock_file->isLocked();
}

