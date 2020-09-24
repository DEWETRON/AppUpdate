# AppUpdate
Notification service and library for handling application updates

# Prerequisites
AppUpdate is a Qt application. To succesfully build it a Qt installation is needed.
Currently we are using Qt 5.12.6 (LTS).

# Directory structure

## cmake

Common cmake settings.

# Compiler

This project successfully builds using:
* Visual Studio 2019
* GCC 8+

# Building

```cmd
mkdir build
cd build
```

For a Visual Studio 2019 run:
```cmd
cmake -G "Visual Studio 16 2019" -DQT_BASE_PATH=../qt/5.12.6_win64 ..
```

Open the generated solution:
```cmd
start AppUpdate.sln
```

# Contact

**Company information**

[www.dewetron.com](https://www.dewetron.com)

**For general questions please contact:**

support@dewetron.com


**For technical questions please contact:**

Michael Oberhofer 

michael.oberhofer@dewetron.com

Gunther Laure

gunther.laure@dewetron.com


# License
GPL-3.0 License 
