# Message structure
The structure of messages exchanged between clients and the server in this application is inspired by the HTTP message structure. They are composed of a sequence of texts encoded in UTF-8.

There are two types of messages: _request messages_ sent by clients to query some information on the server or tell the server to do some action, and _response messages_ sent by the server which contain the data required by clients.

The basic structure of a message is as follow:
```
<header line>
\n\n
<message size>
<data field>
```
* The header line indicates the command and the type of command requested by the clients in the, or the status of the command.
* A blank line to separate the header line and the rest of the message.
* The message size is an integer indicating the size of the message.
* The data field contains the data associated with the command or the response. 

## Request messages
### Header line
The header line of the request messages contains two field:
```<command> [<type>]```
* `command` field: a string describes the action to be performed by the server (one of `login`, `logout`, `signup`, `query`).
* `type` field (optional): a string describes the type of the command requested (e.g. `login admin` tells the server that the user is logging in as an admin.)

### Message size
An integer (represented as a string) indicates the size of the message (in bytes).

### Data field
The `data` field contains the data associated with the command and can be empty (since not all commands required associated data). The structure of the `data` field depends on the command and the type of command.

## Response messages
### Header line
The header line of the response messages also contains two fields:
``` <status code> <status message>```
* `status code`: a three-digit integer (represented as a string) indicates the request is _successful_ or _fail_. The complete list of status codes is in the <>.
* `status message`: a string describes the meaning of the status code.

### Message size
Same as request messages.

### Data field
The `data` field of responses messages contains the data required by the clients. `data` field is empty if the status code is not `000` (means success). Otherwise, it contains the data requested by the clients and its structure also depends on the request made prior by the clients.

# Commands
The commands are divided into six categories: _discover_, _login_, _logout_, _signup_, _query_, and _update_. Each command can have one or more types.

## discover


## login
The **login** command sends to the server a username and a password to signal that the user is logging in. The login command has two types:

### Ordinary user
#### Description
This command request the user to verify the authentication of an ordinary user. If the authentication is successful, the server responses with the username, the user's name, and the weather information of all city in the current day. If the authentication fail, the server responses with status code `1xx`.

#### Type field
`<empty>`

#### Request message data field
```
<username>,<password>
```

#### Response message data field
```
Line 1: <username>,<name>
Line 2: <m>
Line 3: <weather info 1>
Line 4: <weather info 2>
...
Line 2 + m: <weather info m>
```
Where:
* `m`: a non-negative integer indicates the number of weather information included in the data field.
* `weather info`: a comma separated list which has the following elements: `<city_name>,<current date>,<weather description>,<min degree>,<max degree>,<precipitation>`

### Admin
#### Description
This command tells the server that an admin is trying to log in. If the authentication is successful, the server responses with the admin username, name, and the weather information of all cities in the current day.

#### Type field
`admin`

#### Request message data field
```
<username>,<password>
```

#### Response message data field
Same as ordinary user's data field.

## logout
The command **logout** requests the server that the user is logging out. This command has only one type for both ordinary user and admin.

#### Description
Requests the server to log out.

#### Type field
`<empty>`

#### Request message data field
`<empty>`

#### Response message data field
`<empty>`

## signup
The **signup** command register a new user to the database. This command is available to ordinary user only. Admins are predefined.

#### Description
Register a new user.

#### Type field
`<empty>`

#### Request message data field
````
<username>,<password>,<name>
````

#### Response message data field
Same as login's command.

## query
The **query** command is used for searching city by name, retrieving historical weather data, and retrieving weather forecast data for a particular city. This command has three types: _city_, _weather_, and _forecast_.

### Search city
#### Description
Request a list of cities whose names match a particular keyword.

#### Type field
`city`

#### Request message data field
```
<keyword>
```

#### Response message data field
```
Line 1: n
Line 2: <city 1>
Line 3: <city 2>
...
Line n + 1: <city n>
```
Note:
* `n`: A non-negative integer indicates the number of matched city.
* `<city>`: A comma-separated list of `<city id>,<city name>,<country name>`.

### Query historical weather information
#### Description
Retrieve the weather information of all cities in a given date.

#### Type field
`weather`

#### Request message data field
```
<date>
```
Note:
* `<date>` is in YYYY-MM-DD format.

#### Response message data field
Same as ordinary user.

### Forecast
#### Description
Retrieve the 7-day weather forecast information of a given city.

#### Type field
`forecast`

#### Request message data field
```
<city id>
```

#### Response message data field
```
Line 1: n
Line 2: <weather info today>
Line 3: <weather info tomorrow>
...
Line n + 1: <weather info n>
```
Note:
* `n`: An integer (0 &le; `n` &le; 7).
* `<weather info>`: A comma-separated list of `<date>,<min degree>,<max degree>,<precipitation>`.
  * `<date>`: YYYY-MM-DD format.