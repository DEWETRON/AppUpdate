#add_subdirectory(content)

set(QML_FILES
  main.qml
)

add_custom_target(au_qml
  SOURCES ${QML_FILES}
)


# add this to Visual Studio group
set_target_properties(au_qml PROPERTIES FOLDER "qml")
