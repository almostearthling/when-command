# Achievements and Roadmap

List of achievements and expectations for the When applet.


## 1) Reached goals

* Configuration :ok:
  - General configuration file :ok:
  - User configuration directory :ok:
  - Autostart :ok:
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
  6. File Watch :+1:
  7. Generic DBus signal :+1:
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
  - *System-wide* based on `/usr` :+1:
  - *Local* based on `/usr/local` :+1:
  - *Local* based on `/opt` :+1:
  - *User* based on `~/.local/share/when-command` and `~/.local/bin` :+1:
* Generalization of resource locations :ok:
  1. Dialog boxes :+1:
  2. Icons and images :+1:
  3. Theme path :+1:
* Autodetect dark or light system theme :ok:
* Dialogs as resources :ok:
* Delete task :ok:
* Delete condition :ok:
* Resource strings (temporarily local, but moveable) :ok:
* History box :ok:
  1. History list with: :+1:
    - Event time and duration :+1:
    - Triggering condition :+1:
    - Task name :+1:
    - Task result (success/failure) :+1:
    - Failure reason :+1:
  2. Task output pane (changes on list selection) :+1:
* Single instance application (per user) :ok:
* Better logging :ok:
  - Remove excess and redundant cruft :+1:
  - Log limits (size and backups) in configuration :+1:
* Log management :ok:
* Application icon :ok:
* Application `.desktop` entry :ok:
* Ubuntu/Debian package :ok:
* Refactoring: instance variables instead of properties and setters :ok:
* Move initialization calls (not variables) to the `if __name__ == "__main__"` block
* Dialog box design and refactoring :ok:
* Command line switches (and configuration maintenance) :ok:
  - Close current instance  :+1:
  - Open settings dialog  :+1:
  - Clear/Rebuild configuration directory  :+1:
  - Rewrite configuration  :+1:
  - Rewrite configuration and exit (via 2 switches)  :+1:
  - Install icons  :+1:
  - Force indicator icon on  :+1:
  - export tasks and conditions :+1:
  - import tasks and conditions  :+1:
  - export and import DBus signal handlers :+1:
* Regexp match for shell command results (in both tasks and conditions) :ok:
* Stop task sequence upon failure (or success) of one task :ok:
* More system and session event conditions :ok:
  - System suspend and/or resume :+1:
  - Screen lock :interrobang:
  - Screensaver :+1:
  - Storage device attach/detach :+1:
  - Join/Leave network :+1:
* Command-line triggered conditions :ok:
* Generic DBus signal handler conditions :ok:
* File and directory watch conditions :ok:
* Export environment variables with task and condition name :ok:


## 2) To *Working* Alpha Release

**All goals for working alpha have been achieved.**


## 3) To Beta Release

**All goals for beta release have been achieved.**


## 4) To Github Release

**All goals for Github have been achieved.**


## 5) To 1.0 *Production* Release

**All goals for Production Release have been achieved.**


## 6) Desirable features

* Package repository
* Fix GTK warnings (some can't be fixed)
* Icons as specified in https://developer.gnome.org/icon-theme-spec/
* Tests and amendments for other Linux flavors and distributions


## 7) Ongoing actions

* Check code consistency
* Remove unused functions
* Obviously bugfix and maintenance
* UI/UX redesign and evolution
* Flexibility and use cases
