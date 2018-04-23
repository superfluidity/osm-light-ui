from django import template
register = template.Library()

'''
    Custom template filter 
'''
@register.filter
def get(mapping, key):
    result = mapping.get(key, '')
    return result

'''
    Custom template filter 
'''
@register.filter
def get_sub(mapping, args):
    splitted = args.split(',')
    sub_dict = mapping.get(splitted[0], '')
    if isinstance(sub_dict, dict):
        return sub_dict.get(splitted[1], '')
    return ''
