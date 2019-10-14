# -*- coding: utf-8 -*-

'''
    flaskext.yamlconfig
    ~~~~~~~~~~~~~~~~~~~
    
    YAML configurator for Flask app.
    
'''

from __future__ import with_statement

import yaml

from flask import request
from flask import current_app
from flask import render_template

from werkzeug import import_string, cached_property
from werkzeug.wrappers import BaseResponse


__all__ = (
    "Context",
    "ConfigureError",
    "Renderer",
    "LazyView",
    "AppYAMLConfig",
    "register_renderer",
    "install_yaml_config",
)

_RENDERERS = {}

        
class Context(dict):
    """Class for view context
    """
    def __getattr__(self, key): 
        try:
            return self[key]
        except KeyError, k:
            raise AttributeError, k
    
    def __setattr__(self, key, value): 
        self[key] = value
    
    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError, k:
            raise AttributeError, k
    
    def __repr__(self):     
        return '<Context ' + dict.__repr__(self) + '>'

        
class LazyView(object):
    '''Lazyloading view
    '''

    def __init__(self, import_name):
        self.__module__, self.__name__ = import_name.rsplit('.', 1)
        self.import_name = import_name

    @cached_property
    def view(self):
        return import_string(self.import_name)

    def __call__(self, *args, **kwargs):
        return self.view(*args, **kwargs)
       

       
def register_renderer(name, renderer_class):
    '''Register renderer
    '''
    if name in _RENDERERS:
        raise ConfigureError('Renderer `%s` allready registered.' % name)
    _RENDERERS[name] = renderer_class

    
    

class ConfigureError(ValueError):
    """Configuration exception
    """
    
    
class Renderer(object):
    '''Base Renderer class
    '''
    
    def __init__(self, view_func, context):
        self.view_func = view_func
        self.context = context
        
    def __call__(self, **kw):
        '''Run renderer'''
        self.context.update(kw)
        view_result = self.view_func(self.context, request, **kw)
        if isinstance(view_result, BaseResponse):
            return view_result
        return self.render(view_result)
        
    def render(self, view_result):
        '''Override in subclass
        '''
        raise NotImplementedError('Renderer.render must be override.')
    
    
    
class PassRenderer(Renderer):
    """Only pass context & request to view_func
    """
    def render(self, view_result):
        return view_result
    
    
class JinjaRenderer(Renderer):
    """Templating view_func result
    """
    def __init__(self, view_func, context, template):
        Renderer.__init__(self, view_func, context)
        self.template = template
        
    def render(self, view_result):
        ctx = self.context.copy()
        ctx.update(view_result)
        return render_template(self.template, **ctx)


def configure_views(app, views):
    """Configure views
    """

    def configure_view(endpoint, options):
        """Configure view
        """
    
        context = Context()
        if 'context' in options:
            context.update(options.pop('context'))
        
        view_func = options.pop('view', None)
        if view_func is None:
            raise ConfigureError('Required field `view` missing.')
        view_func = LazyView(view_func)
            
        rules = options.pop('url', [])
        if not isinstance(rules, list):
            rules = [rules]
            
        renderer_class, renderer = None, options.pop('renderer', None)
        
        if not renderer is None:
            renderer_class = _RENDERERS.get(renderer, None)
            
        if renderer_class:
            view_func = renderer_class(view_func, context)
        elif renderer:
            view_func = JinjaRenderer(view_func, context, renderer)
        else:
            view_func = PassRenderer(view_func, context)
  
        for rule in rules:
            app.add_url_rule(rule, endpoint, view_func, **options)
    
    # begin 
    for view_name in views:
        configure_view(view_name, views[view_name])
        
        

class AppYAMLConfig(object):
    """App YAML configurator
    """

    def __init__(self, app, conf_file=None):
        self.app = app
        if conf_file:
            self.load(conf_file)
        
    def __call__(self, conf_file):
        with self.app.open_resource(conf_file) as cfd:
            conf = yaml.load(cfd.read())
        for section in conf:
            meth = 'configure_%s' % section
            if not hasattr(self, meth):
                raise ConfigureError('Unknown section `%s`.' % section)
            meth = getattr(self, meth)
            meth(conf[section])
            
    load = __call__
            
    def configure_include(self, files):
        '''include: section'''
        for yaml_file in files:
            self.load(yaml_file)
                
    def configure_application(self, obj):
        '''application: section'''
        self.app.config.from_object(type('', (object,), obj))
            
    def configure_views(self, views):
        '''views: section'''
        configure_views(self.app, views)
            
            
   
def install_yaml_config(app, conf_file=None, configurator_class=AppYAMLConfig):
    """Install YAML configurator
    """
    if not issubclass(configurator_class, AppYAMLConfig):
        raise ConfigureError('`configurator_class` must be of subcalss of `AppYAMLConfig`')
    return configurator_class(app, conf_file)
    