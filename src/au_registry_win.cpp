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

#include "au_registry_win.h"

#ifdef WIN32
#include "windows.h"
#include <strsafe.h>
#endif

AuRegistry::AuRegistry()
{
}

AuRegistry::~AuRegistry()
{
}

#ifdef WIN32


bool AuRegistry::enumInstalledSoftware()
{
    HKEY hUninstKey = NULL;
    HKEY hAppKey = NULL;
    char sAppKeyName[1024];
    char sSubKey[1024];
    char display_name[1024];
    char display_version[1024];
    char publisher[1024];

    std::vector<const char*> registry_root = {
        "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall",
        "SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall"
    };

    long lResult = ERROR_SUCCESS;
    DWORD dwType = KEY_ALL_ACCESS;
    DWORD dwBufferSize = 0;

    m_installed_sw.clear();

    std::vector<SwEntry> all_sw_entries;

    for (const auto sRoot : registry_root)
    {

        //Open the "Uninstall" key.
        if (RegOpenKeyEx(HKEY_LOCAL_MACHINE, sRoot, 0, KEY_READ, &hUninstKey) != ERROR_SUCCESS)
        {
            return false;
        }

        lResult = ERROR_SUCCESS;

        for (DWORD dwIndex = 0; lResult == ERROR_SUCCESS; dwIndex++)
        {
            //Enumerate all sub keys...
            dwBufferSize = sizeof(sAppKeyName);
            if ((lResult = RegEnumKeyEx(hUninstKey, dwIndex, sAppKeyName,
                &dwBufferSize, NULL, NULL, NULL, NULL)) == ERROR_SUCCESS)
            {
                //Open the sub key.
                sprintf(sSubKey, "%s\\%s", sRoot, sAppKeyName);
                if (RegOpenKeyEx(HKEY_LOCAL_MACHINE, sSubKey, 0, KEY_READ, &hAppKey) != ERROR_SUCCESS)
                {
                    RegCloseKey(hAppKey);
                    RegCloseKey(hUninstKey);
                    return false;
                }

                //Get the display name value from the application's sub key.
                dwBufferSize = sizeof(display_name);
                if (RegQueryValueEx(hAppKey, "DisplayName", NULL,
                    &dwType, (unsigned char*)display_name, &dwBufferSize) != ERROR_SUCCESS)
                {
                    //Display name value does not exist, this application was probably uninstalled.
                    RegCloseKey(hAppKey);
                    continue;
                }

                dwBufferSize = sizeof(display_version);
                if (RegQueryValueEx(hAppKey, "DisplayVersion", NULL,
                    &dwType, (unsigned char*)display_version, &dwBufferSize) != ERROR_SUCCESS)
                {
                    //Display version value does not exist, this application was probably uninstalled.
                    RegCloseKey(hAppKey);
                    continue;
                }

                dwBufferSize = sizeof(publisher);
                if (RegQueryValueEx(hAppKey, "Publisher", NULL,
                    &dwType, (unsigned char*)publisher, &dwBufferSize) != ERROR_SUCCESS)
                {
                    //Publisher value does not exist, this application was probably uninstalled.
                    RegCloseKey(hAppKey);
                    continue;
                }

                all_sw_entries.push_back({ display_name, display_version, publisher });

                RegCloseKey(hAppKey);
            }
        }

        RegCloseKey(hUninstKey);
    }

    // Filter company products
    for (const auto& sw : all_sw_entries)
    {
        if (sw.m_publisher.find("DEWETRON") != std::string::npos)
        {
            m_installed_sw.push_back(sw);
        }
    }

    return true;
}
#else
bool AuRegistry::enumInstalledSoftware()
{
    return true;
}
#endif


std::vector<SwEntry> AuRegistry::getInstalledSw() const
{
    return m_installed_sw;
}
