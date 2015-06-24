# Achievements and Roadmap

List of achievements and expectations for the When applet.


## 1) Reached goals

* Configuration :ok:
  - General configuration file :ok:
  - User configuration directory :ok:
* Tasks :ok:
  1. Shell command execution :ok:
  2. Import environment variables upon request :ok:
  3. Set specific environment variables :ok:
  4. Check for specific success or failure conditions :ok:
* Conditions :ok:
  1. Time :+1:
  2. Interval :+1:
  3. Command :+1:
  4. Idle :+1:
  5. Event :+1:
* One time or repeated condition checks :ok:
* Parallel or sequential task execution :ok:
* Functioning task definition box :ok:
* Functioning condition definition box :ok:
* Scheduler :ok:
* Indicator icon :ok:
* Pause/Resume :ok:
* Pause/Resume icon :ok:
* Settings dialog box :ok:
* Reconfigure on the fly [*partial*] :ok:
* About box :ok:
* Task startup directory chooser box :ok:
* Suspend condition :ok:
* Notifications (when activated) :ok:
* Icon change on task failure (when notifications are active) :ok:
* *System-wide* vs *Local* vs *User* installation (*to be tested*) :ok:
  - *System-wide* based on `/usr` :ok:
  - *Local* based on `/usr/local` :ok:
  - *Local* based on `/opt` :ok:
  - *User* based on `~/.local/share/when-command` and `~/.local/bin` :ok:
* Generalization of resource locations :ok:
  1. Dialog boxes :ok:
  2. Icons and images :ok:
  3. Theme path :ok:
* Autodetect dark or light system theme :ok:
* Dialogs as resources :ok:
* Delete task :ok:
* Delete condition :ok:
* Resource strings (temporarily local, but moveable) :ok:
* History box :ok:
  1. History list with: :ok:
    - Event time and duration :ok:
    - Triggering condition :ok:
    - Task name :ok:
    - Task result (success/failure) :ok:
    - Failure reason :ok:
  2. Task output pane (changes on list selection) :ok:
* Single instance application (per user) :ok:
* Better logging :ok:
  - Remove excess and redundant cruft :ok:
  - Log limits (size and backups) in configuration :ok:
* Log management :ok:
* Application icon :ok:
* Application `.desktop` entry :ok:


## 2) To *Working* Alpha Release

**All goals for working alpha have been achieved.**


## 3) To Beta Release

**All goals for beta release have been achieved: testing is on the way.**


## 4) To Github Release

**All goals for Github have been achieved.**


## 5) To 1.0 *Production* Release

* Refactor dialog boxes
  1. Control names
  2. Static control naming conventions (labels, boxes, spacers, etc.)
  3. More modern controls, especially for compound values (e.g. Time)
  4. Numeric values via spin buttons
* Better dialog box design
  - Enable/disable controls depending on options in menus and combo boxes
  - Set default values for unselected controls when choosing condition type
  - Set default values for unselected controls when choosing event type
  - Time condition time definition line
  - Better control shapes and types
  - Use a more homogeneous design (padding, spacing, fill, etc.)
* Clean up code
  - Use instance variables instead of properties and setters
  - Fix GTK errors
* Ubuntu/Debian package


## 6) Desirable features

* Modal dialog boxes
* System event conditions
* File watch conditions
* Stop task sequence upon failure (or success) of one task
* Configuration directory maintenance tools
* Package repository
* Icons as specified in https://developer.gnome.org/icon-theme-spec/


## 7) Cyclic development actions

* Check code consistency
* Remove unused functions
