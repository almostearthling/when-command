# Generated Configuration File

Some notes follow about the **whenever** configuration files generated by **When**.

* The generated configuration files are well-formed TOML files: this means, for instance, that they can be re-edited by hand and, if the result is still well-formed and compliant to the format used by **whenever**, used to configure the scheduler. However there are some peculiarities that have to be taken into account:
  * the strings and arrays generated by **When** are all one-liners: it is possible to convert them to multiline arrays and strings, and **When** wil be able to read and edit the resulting files without problems, but this human-readable formatting is lost for all item definitions as soon as **When** rewrites the configuration file: as a consequence, one-line strings will contain escaped characters when needed;
  * TOML tables, on the other hand, are written using the TOML extended format (thus not as one-line pair sequences enclosed in curly braces), even for simple and short mappings: any conversion of tables into the simpler, one-line format can be read by **When** but is lost also in this case if the file is rewritten.
* **When** uses the `tags` configuration entry for specialized items built on top of the ones that are native to **whenever**: of course, it also sets the standard parameters known to **whenever** (it ignores the contents of the `tags` entry), and the user can modify any of these standard parameters by hand if needed: **whenever** will obey these changes when using the resulting configuration files even when it is launched using **When** as frontend; however, as soon as **When** re-reads the file for editing, it will ignore all the changes that have been made to the standard parameters and reuse the ones that are calculated according to the values stored in the `tags` section.
* Since the files generated by **When** are just standard **whenever** oriented configuration files, they can be used with any frontend and even with no frontend at all, by just respectively instructing the chosen frontend (for example, **whenever_tray**) or **whenever** itself to use the _%APPDATA%\Whenever\whenever.toml_ or _~/.whenever/whenever.toml_ configuration file depending on the host platform.

This means, for instance, that **When** can also be used as a way to start configuring the scheduler only for the first time, and that the resulting configuration file can then be edited and enhanced manually to suit the user's needs. Also note that if the `tags` table is completely removed from the definition of an item, _that item will still work_ in **whenever**. The only drawback is that **When** will not be able to edit that item using the specific editor and, _if supported_, the editor for the corresponding standard item is used.


[`◀ Main`](main.md)