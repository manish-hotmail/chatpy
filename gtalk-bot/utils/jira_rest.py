""" Provides wrapper over the jira-python 0.12 lib
"""
import sys


#Patch to use different Jira Rest libs
JIRA_REST_LIB_NAME = 'jira_python-0.12-py2.7.egg'
sys.path = [e_p for e_p in sys.path if JIRA_REST_LIB_NAME not in e_p]
sys.path.append('/home/whops/python-extra-libs')
##print '\npythonpath', sys.path

from jira.client import JIRA

def get_jira_session(jira_server, jira_user, jira_password):
    """ Creates JIRA session and returns it.
    """
    jira = JIRA(options={'server': jira_server, 'verify': False}, basic_auth = (jira_user, jira_password))
    return jira
    
def create_jira_issue(jira, is_test, jira_project, jira_issuetype, jira_assignee, 
                      summary, description, severity_value = None, environment_value = None, 
                      components = None, watchers = None,
                      jira_timetracking = None, jira_duedate = None, priority=None):
    """ Creates JIRA issue and returns new ticket.
        @param is_test: boolean value to create real jira ticket or not. If False given then returns dummy 'jira_test' object having key='NA'.
        @param watchers: list of JIRA user names. 
    """
    #Patch for Jira create API to avoid unnecessary Jira ticket creation during testing. Returns fake_jira with 'key' attribute.
    if is_test:
        class jira_test(object):
            key = 'NA'
        return jira_test

    pm_jira_dict = {
                'project': {'key': jira_project},
                'summary': summary,
                'description': description,
                'issuetype': {'name': jira_issuetype},
                'assignee':{'name': jira_assignee}
                }
    
    if priority:
        pm_jira_dict['priority'] = {'name': priority}
        
    if severity_value:
        pm_jira_dict['customfield_10021'] = {'value': severity_value}
        
    if environment_value:
        pm_jira_dict['customfield_10022'] = [{'value': environment_value}]
        
    if components:
        pm_jira_dict['components'] = [{'name': components}]
        
    if jira_timetracking:
        pm_jira_dict['timetracking'] = {'originalEstimate': jira_timetracking}

    if jira_duedate:
        pm_jira_dict['duedate'] = jira_duedate

    new_issue = jira.create_issue(fields=pm_jira_dict)

    for each_user in watchers:
        jira.add_watcher(issue=new_issue.key, watcher=each_user)
        
    return new_issue
    

class JiraRest(object):
    """
    """
    def __init__(self, jira_server, jira_user, jira_password, verify = False):
        self._jira_server = jira_server
        self._jira_user = jira_user
        self._jira_password = jira_password
        self._verify = verify
        self.is_alive = False
        self._jira = False
    
    def _get_session(self):
        """ Creates JIRA session and returns it.
        """
        jira = JIRA(options={'server': self._jira_server, 'verify': self._verify}, \
                                            basic_auth = (self._jira_user, self._jira_password))
        if jira:
            try:
                jira.session().raw['name']
                self.is_alive = True
                self._jira = jira
            except:
                self.is_alive = False
                self._jira = False
        else:
            self.is_alive = False
            self._jira = False
            
        return self._jira
        
    def _refresh_session(self):
        if self.is_alive:
            try:
                self._jira.kill_session()
            except:
                pass
        
        return self._get_session()
    
    def close(self):
        if self.is_alive:
            try:
                self._jira.kill_session()
            except:
                pass
        
        self.is_alive = False
        self._jira = False
        
    def __del__(self):
        self.close()
        
    def get_session(self):
        if self.is_alive:
            try:
                self._jira.session().raw['name']
            except:
                self.close()
                self._get_session()
        else:
            self._get_session()
            
        return self._jira
        
    def get_session_status(self):
        return self.is_alive
        
    def create_jira_issue(self, jira, is_test, jira_project, jira_issuetype, jira_assignee, 
                          summary, description, severity_value = None, environment_value = None, 
                          components = None, watchers = None,
                          jira_timetracking = None, jira_duedate = None, priority=None):
        """ Creates JIRA issue and returns new ticket.
            @param is_test: boolean value to create real jira ticket or not. If False given then returns dummy 'jira_test' object having key='NA'.
            @param watchers: list of JIRA user names. 
        """
        #Patch for Jira create API to avoid unnecessary Jira ticket creation during testing. Returns fake_jira with 'key' attribute.
        if is_test:
            class jira_test(object):
                key = 'NA'
            return jira_test
    
        pm_jira_dict = {
                    'project': {'key': jira_project},
                    'summary': summary,
                    'description': description,
                    'issuetype': {'name': jira_issuetype},
                    'assignee':{'name': jira_assignee}
                    }
        
        if priority:
            pm_jira_dict['priority'] = {'name': priority}
            
        if severity_value:
            pm_jira_dict['customfield_10021'] = {'value': severity_value}
            
        if environment_value:
            pm_jira_dict['customfield_10022'] = [{'value': environment_value}]
            
        if components:
            pm_jira_dict['components'] = [{'name': components}]
            
        if jira_timetracking:
            pm_jira_dict['timetracking'] = {'originalEstimate': jira_timetracking}
            
        if jira_duedate:
            pm_jira_dict['duedate'] = jira_duedate
            
        self.get_session()
        new_issue = self._jira.create_issue(fields=pm_jira_dict)
        
        for each_user in watchers:
            self._jira.add_watcher(issue=new_issue.key, watcher=each_user)
            
        return new_issue
    
