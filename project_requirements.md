### **ToDos**
# Learners Environment


## Flags

***[clients]* Use flags to track exercise progress**

In order to better track the learning progress of the participants, flags are stored in relevant files that the participant will find if he proceeds accordingly (plus optional steps). These must then be registered by the user in a local file, which is then checked by venjix.


***[clients]* Add *add_flag* script to hosts**

A script that checks the flag format (similar to CTF challenges) and appends it to a specific file.

The user can add a flag by simply executing the following command:
```bash
addflag *found_flag*
```


***[venjix]* Implement flag-tracking**

When calling "check" via the Learners interface, the flag file on the client is queried and checked in addition to the simple pass check. venjix then forwards the result to the Learners interface accordingly.


***[learners]* Accept additional response-fields from venjix**

The Learners interface must be able to display the result it has received from venjix. While the exercise is not yet solved, the progress should only be displayed via a progress bar. Only after the pass-check all possible flags with the corresponding check/non-check are displayed.

-------------------------- 

 ## Modular design

The Learners environment must be modular so that the individual components can be activated/deactivated. For example, it should also be possible to use the Learners environment without VNC access or to start without chat support.

--------------------------

## Further ToDos

***[learners]* Implement Mattermost client**

A lightweight Mattermost REST client needs to be implemented that first supports the basic Mattermost functionality and can be integrated into the Learners environment.


***[ansible-learners]* use hugo config.toml to deploy user-based exercises**

Currently the deployment of the exercises and the docu is controlled by a detour via the control-host, but for this the config.toml of hugo should be used.


***[ansible-flask]* offer dotenv to configure flask apps **

Flask applications must also be configurable via dotenv files.


***[ansible-mattermost]* write ansible module for mattermost configuration**

To avoid having to access error messages via ansible, an extra module must be written for managing mattermost.


--------------------------