'''
Created on Apr 20, 2016

@author: caleb kandoro
'''
'''
Created on Apr 4, 2016

@author: caleb kandoro

provides a quick and easy way to create htm files especially forms
imitates the dom principles  with attributes 
there is a hierarchy of objects with parent children relationships.
the lowest items store a reference to their parents and are immediately added to them
upon creation
objects with both parents and children(form, fieldset) need a create_<tag> method call 
to be added to their parents after ALL their children have been enumerated

'''

templating = False


class Document():
    def __init__(self):
        self.children = []
        self.css = ''
        self.script = ''
        

    def add_elemet(self, element):
        '''used to add hard coded children into the document'''
        self.children.append(element)
        
        
    def create_document(self, file_name):
        """takes a filename mandatory argument"""
        fil = open(file_name, "w")
        self.create_content()
        if templating:
            fil.write("""
            <!Doctype html>
            <html>
                <head>
                    <link rel= "stylesheet" href = "{css}">
                    {script}
                </head>
                <body>
                    <div id="container">
                    {content}
                    </div>
                </body>
            </html>""".format(script = self.script, css= self.css, \
                              content = self.content))
        
        else: 
            fil.write(self.content)
            
    def create_content(self):
        
        self.content = "\n\t".join(self.children)
    
    def create_menu(self, _items = []):
        list_items = []
        for _item in _items:
            list_item = """<li><a href="{i}">{i}</a></li>
                        """.format(i=_item)
            list_items.append(list_item)
        
        menu = '''<div id ="menu">
                    <ul>{}</ul>
                    </div>
                    '''.format("\n\t".join(list_items))
                    
        self.children = [menu] + self.children
        
            
class form():
    def __init__(self, document,action, button ):
        self.children = []
        self.method = "GET"
        self.action = action
        self.button = button
        self.parent = document 
        self.base_string  = """<form method="{}" action="{}">
                            {}
                            <button>{}</button>
                            </form>
                        """
        
    def add_element(self, element):
        '''for hard coded additions to the form'''
        self.children.append(element)
        
    def create_elements(self):
        return "\n\t".join(self.children)
    
    def create_form(self):
        self.parent.children.append( self.base_string.format(self.method,
                                       self.action,
                                       self.create_elements(),
                                       self.button))
        
class fieldset():
    def __init__ (self, parent, name):
        self.name = name
        self.parent = parent
        self.children = []
        self.base_string = """<fieldset>
                                <legend>{}</legend>
                                {}
                                </fieldset>
                        """
                        
    def add_element(self, element):
        self.children.append(element)
        
        
    def create_elements(self):
        return "\n\t".join(self.children)

                
    def create_fieldset(self):
        '''must call this method to actually create the fieldset'''
        self.parent.children.append \
                (self.base_string.format \
                 (self.name, self.create_elements()))
    
    
    
class text():
    def __init__(self, parent, name):
        '''creates text box that is similar
        to a textarea'''
        self.name = name
        self.parent = parent
        self.create_text()
        
    def create_text(self):
        self.parent.children.append("""{name}:
        <input name ="_{name}" id="__{name}" type= "text">
        """.format(name =self.name))
        
class textarea():
    def __init__(self, parent, name):
        '''creates textarea that is similar
        to a text'''
        self.name = name
        self.parent = parent
        self.create_textarea()
        
    def create_textarea(self):
        self.parent.children.append("""{name}:
        <input name ="_{name}" id="__{name}" type= "textarea">
        """.format(name=self.name))        
        
        
class selectbox():
    def __init__(self, parent, items = []):
        '''the class creates a selectbox based 
            on the list of options provided'''
        option_list = ["<option value = _{item}>{item}</option>".format(item=item) \
                        for item in items]
        self.parent = parent
        self.option_string = "\n\t".join(option_list)
        self.create_selectbox()
        
        
    def create_selectbox(self):
        self.parent.children.append("""<select>
                    {}
                </select>""".format(self.option_string))
                
                

if __name__ == "__main__":
    d = Document()
