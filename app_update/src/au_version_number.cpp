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

#include "au_version_number.h"

AuVersionNumber::AuVersionNumber()
    : m_qversion()
    , m_suffix()
{
}

AuVersionNumber::AuVersionNumber(const QVersionNumber& qver, const QString& sfx)
    : m_qversion(qver)
    , m_suffix(sfx)
{
}

QString AuVersionNumber::toString() const
{
    if (m_suffix.isEmpty()) return m_qversion.toString();
    return QString("%1 %2").arg(m_qversion.toString(), m_suffix);
}

AuVersionNumber AuVersionNumber::fromString(const QString& ver_string)
{
    int index = 0;
    QVersionNumber qver = QVersionNumber::fromString(ver_string, &index);
    QString sfx = ver_string.mid(index).trimmed();
    return { qver, sfx };
}

bool operator>(const AuVersionNumber& lhs, const AuVersionNumber& rhs)
{
    if (lhs.m_qversion == rhs.m_qversion)
    {
        // no suffix means Release vs Release Candidate
        if (lhs.m_suffix.isEmpty()) return true;
        if (rhs.m_suffix.isEmpty()) return false;
        return lhs.m_suffix > rhs.m_suffix;
    }
    return lhs.m_qversion > rhs.m_qversion;
}
