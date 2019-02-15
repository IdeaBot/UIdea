# UIdea #
IdeaBot add-ons package for user interfaces using Discord embeds.

## What? ##
Text commands are so last century.
Graphical User Interfaces (GUIs) are the future (and the past and the present).

Text-based terminals were replaced by GUIs ages ago, but Discord bots still rely on text commands.
IdeaBot's UIdea package aims to fix that by using Discord embeds to offer users an intuitive and easy-to-use way to interact with the bot.

## Overview ##
UIdea is a collection of plugins, commands and reaction-commands to make user interaction easy.

UIdea is a toolkit to enable others to create UIs, so UIdea does not have any concrete commands for users. Most valid commands are defined by user-made UIs, but I can't document infinite possibilities.

Nevertheless, there is one important command to know.

### Commands ###
* UI
> Get helpful information on UIs

# Documentation #

## Getting Started ##
UIdea uses a design similar to Android Activities; it uses two files to describe how the UI behaves.
One file describes the starting layout and behaviour of the UI while the other file describes the functionality of the UI.

The first file is a JSON file, ending with `.json`, which contains information about your UI. The default UI JSON, `data/default_uidea_json.json`, shows the structure.
Any value can be removed except for information under "version", which are required to load the UI properly.
Any missing value will be set to the default value from the default UI JSON file. Make sure you save your UI JSON file in the `addons` folder or a direct subfolder (ie `addons/my_package`). [More information here](https://github.com/IdeaBot/UIdea/tree/master#ui-json-file).

The second file is a Python file, ending with `.py`, which contains the UI class and methods to handle button (reaction) clicks and other inputs.
The method in the UI class which will be called on button clicks (or other inputs) is the method name entered in your UI's json file.
To modify the UI, modify the embed object stored in the variable `self.embed`.
To update the UI (after modifying the embed), use `self.update()`.
[More information here](https://github.com/IdeaBot/UIdea/tree/master#ui-python-file).

For more information, see the full documentation of both files below.

## UI JSON File ##
See `data/default_uidea_json.json` for the full layout of a JSON file.
Please note that missing values will be filled with values from the default file.
Certain values are required and will not be automatically filled.
If a required value is missing, the UI won't be loaded.
To see skipped files, open `data/UIdea.log`.

To see a working example, check out `pages.json` and `UIs/pages.py`. Send a message containing `I'd like to read` to try it out.

### Keys ###
*-required

**version***: dict; contains:
* **api***: str; API version number. Accepted values: `v0.0.1`.
* **type***: str; Must be `ui-json`, otherwise the file will be skipped.

**info**: dict; contains:
* **name**: str; the name of your UI.
* **description**: str; the description of your UI.
* **help**: str; the message to be displayed when someone does `@Idea help UI <your UI name>`.
* **package**: str; the package your UI belongs to, in order to provide the correct `self.public_namespace` object.
* **filepath**: str; the filepath to your UI's Python file. **CANNOT BE null!**
* **maintainers**: list of str; contains IDs of Discord users you trust to maintain your UI.
* **owner**: str; your Discord ID

**lifespan**: int; the length of time, in seconds, of non-interaction before an instance of your UI is deleted.

**persistence**: bool; whether UI instances should persist between restarts.

**private**: bool; whether more than one person can interact with an instance of your UI.

**shouldCreate**: str; the name of UI method which determines whether a new UI instance should be created. **CANNOT BE null!**

**onCreate**: str; the name of the UI method which initializes the UI instance. **NOT `__init__`!**

**onDelete**: str; the name of the UI method which handles the UI's final duties.

**onPersist**: str; the name of the UI method to be called when the UI is reloaded.

**onReaction**: dict; contains key : value of emoji : UI method called on emoji click.

**defaultEmbed**: dict; contains information to create the initial embed. Very similar to `Embed.to_dict()`.

**debug**: list of str; contains debug flags.

> **__Pro tips__**:
>
> * set onCreate, onDelete, onPersist or onReaction to null to disable them.
>
> * Omit keys to use their default value (except required keys & values).

## UI Python File ##
This file must define a UI class which should be a subclass of `libs.ui.UI`.
To accomplish that, start your file with this:
```Python
from addons.UIdea.libs import ui as ui_class

# your UI class
class UI(ui_class.UI):
  # your methods, as defined in your UI JSON file
  pass
```
Don't worry about `pass` - it's only there to make sure that the file doesn't raise a SyntaxError. Once you've added a body to your UI class, you can safely delete `pass`.

The UI class is quite simple, but it does contain a few pre-defined attributes to allow for it to function. Those attributes are explained below.

To see a working example, check out `pages.json` and `UIs/pages.py`. Send a message containing `I'd like to read` to try it out.

### Default UI Class Attributes ###
These attributes do not need to be defined in your UI class (provided you extended the UI class like the code snippet above), but they shouldn't be deleted either.

* **self.embed** : Embed
> The discord Embed object displayed by the UI.
> Modify this to modify the UI's appearance.

* **self.getEmbed()** : Embed
> Helper method to retrieve the embed.
> This is called by self.update() to retrieve the Embed object.
> NOTE: use self.embed to get the embed
>
> **returns** the embed to be displayed in Discord

* **self.update()** : None
> Updates the UI message with the modified Embed object
> This should not be overridden.

### Custom UI Class Methods ###
These are the methods named in your UI JSON file. They may have different names, but their parameters will always be as described here.

* **onCreate(self, message)** : None
> Initializes the UI instance.
> This method is called once the entire UI instance (message, reactions, etc.) is set up.
>
> **message** : discord.Message object that shouldCreate evaluated to be True.

* **onDelete(self)** : None
> Handle UI data cleanup.
> This method is called when a UI instance is about to be deleted.
> NOTE: This method should cleanup any custom data which may remain after the UI instance is deleted.
> You do not need to worry about the UI instance's object, message or storage.

* **onPersist(self)** : None
> Handle persistence of custom objects.
> This method is called when a UI instance is reloaded.

* **onReaction(self, reaction, user)** : None
> Handle a reaction (button) click.
> This is called whenever the correct reaction is added *or* removed from a UI message.
>
> **reaction** : discord.Reaction object of the Reaction.
>
> **user** : discord.User object of the user who clicked the reaction button.

* **shouldCreate(messsage)** : bool
> Determines if a new UI instance should be created.
> This method is called whenever a message is sent.
> NOTE: self is not a parameter, since shouldCreate is called before a UI instance is create.
>
> **message** : discord.Message object.
>
> **returns** if UI should be created in response to the message.
