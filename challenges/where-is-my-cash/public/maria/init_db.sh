FLAG=${FLAG:-"ALLES{s4mp13_f14g}"}
SQL_SCRIPT=/docker-entrypoint-initdb.d/init_db.sql

echo "Setting flag ${FLAG} in ${SQL_SCRIPT}"
FLAG=`printf '%s\n' "${FLAG}" | sed -e 's/[\/&]/\\&/g'`
sed -i "s/__FLAG__/${FLAG}/" ${SQL_SCRIPT}

IT_PASSWORD=`head -c 50 /dev/urandom | sha256sum | cut -f1 -d" "`
IT_API_KEY=`head -c 50 /dev/urandom | sha256sum | cut -f1 -d" " | head -c 30`
ADMIN_PASSWORD=`head -c 50 /dev/urandom | sha256sum | cut -f1 -d" "`
ADMIN_API_KEY=`head -c 50 /dev/urandom | sha256sum | cut -f1 -d" " | head -c 30`
FRIEND_PASSWORD=`head -c 50 /dev/urandom | sha256sum | cut -f1 -d" "`
FRIEND_API_KEY=`head -c 50 /dev/urandom | sha256sum | cut -f1 -d" " | head -c 30`

echo "Setting passwords and api keys in ${SQL_SCRIPT}"
sed -i "s;__IT_PASSWORD__;${IT_PASSWORD};" ${SQL_SCRIPT}
sed -i "s;__IT_API_KEY__;${IT_API_KEY};" ${SQL_SCRIPT}
sed -i "s;__ADMIN_PASSWORD__;${ADMIN_PASSWORD};" ${SQL_SCRIPT}
sed -i "s;__ADMIN_API_KEY__;${ADMIN_API_KEY};" ${SQL_SCRIPT}
sed -i "s;__FRIEND_PASSWORD__;${FRIEND_PASSWORD};" ${SQL_SCRIPT}
sed -i "s;__FRIEND_API_KEY__;${FRIEND_API_KEY};" ${SQL_SCRIPT}
