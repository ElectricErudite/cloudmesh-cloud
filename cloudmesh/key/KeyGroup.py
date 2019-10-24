from cloudmesh.common.parameter import Parameter
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate

class KeyGroupDatabase:

    # noinspection PyShadowingBuiltins
    def __init__(self, cloud="local", kind="keygroup"):
        self.kind = kind
        self.cloud = cloud
        self.cm = CmDatabase()
        self.collection = f"{self.cloud}-{kind}"

    def clear(self):
        self.cm.collection(self.collection).delete_many({})

    def find(self, name=None):

        if name is None:
            query = {}
        else:
            query = {'cm.name': name}
        entries = self.cm.find(collection=self.collection, query=query)
        return entries

    def remove(self, name=None):

        if name is None:
            query = {}
        else:
            query = {'cm.name': name}
        entries = self.cm.delete(collection=self.collection,
                                 **query)
        return entries

    # noinspection PyBroadException
    def list(self, name=None):
        found = []
        if name is None:
            # find all groups in the db
            found = self.find()
        else:
            # find only the groups specified in the db
            groups = Parameter.expand(name)
            # noinspection PyUnusedLocal
            for group in groups:
                # noinspection PyUnusedLocal
                try:
                    entry = self.find(name=name)[0]
                    found.append(entry)
                except Exception as e:
                    pass

        return found

    def update_dict_list(self, entries):
        for entry in entries:
            entry['cm'] = {
                "kind": self.kind,
                "name": entry['name'],
                "cloud": self.cloud
            }
        return entries

class KeyGroup(KeyGroupDatabase):
    output = {
        "all": {
            "sort_keys": ["group", "rule"],
            "order": ["group",
                      "rule",
                      "protocol",
                      "ports",
                      "ip_range"],
            "header": ["Group",
                       "Rule",
                       "Protocol",
                       "Ports",
                       "IP Range"]
        },
        "key_rule": {
            "sort_keys": ["name"],
            "order": ["name",
                      "protocol",
                      "ports",
                      "ip_range"],
            "header": ["Name",
                       "Protocol",
                       "Ports",
                       "IP Range"]
        },
        "keygroup": {
            "sort_keys": ["name"],
            "order": ["name",
                      "rules",
                      "description"],
            "header": ["Name",
                       "Rules",
                       "Description"]
        }

    }

    def __init__(self, cloud="local"):
        super().__init__(cloud, kind="keygroup")

    # noinspection PyBroadException
    @DatabaseUpdate()
    def add(self,
            name=None,
            rules=None,
            description=None):
        """
        adds a rule to a given group. If the group does not exist, it will be
        created.

        :param name:
        :param rules:
        :param description:
        :return:
        """

        new_rules = rules
        if type(rules) == str:
            new_rules = Parameter.expand(rules)
        elif type(rules) == list:
            pass
        else:
            raise ValueError("rules have wrong type")

        # noinspection PyUnusedLocal
        try:
            entry = self.find(name=name)[0]
        except Exception as e:
            entry = {
                'description': None,
                'rules': [],
                'name': name
            }

        if rules is not None:
            old = list(entry['rules'])
            entry['rules'] = list(set(new_rules + old))

        if description is not None:
            entry["description"] = description

        return self.update_dict_list([entry])

    @DatabaseUpdate()
    def delete(self, name=None, rules=None):
        """
        deletes the groups
        :param name:
        :param rules:
        :return:
        """

        delete_rules = rules
        if type(rules) == str:
            delete_rules = Parameter.expand(rules)
        elif type(rules) == list:
            pass
        else:
            raise ValueError("rules have wrong type")
        delete_rules = set(delete_rules)

        entry = self.find(name=name)[0]

        if rules is not None:
            old = set(entry['rules'])
            old -= delete_rules
            entry['rules'] = list(old)

        return entry
