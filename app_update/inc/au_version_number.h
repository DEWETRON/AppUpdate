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

#include <QVersionNumber>

/**
 * AuVersionNumber is a QVersionNumber with additional string suffix support "RC1"
 */
class AuVersionNumber
{
    friend bool operator>(const AuVersionNumber&, const AuVersionNumber&);

public:
    AuVersionNumber();
    AuVersionNumber(const QVersionNumber& qver, const QString& sfx);

    QString toString() const;

    static AuVersionNumber fromString(const QString& ver_string);

private:
    QVersionNumber m_qversion;
    QString m_suffix;
};


bool operator>(const AuVersionNumber& lhs, const AuVersionNumber& rhs);

