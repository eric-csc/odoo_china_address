{
    "name" : "Odoo Import China Address",
    "version" : "1.0",      
    "author" : "huaguoshan OpenERP team",   
    "website" : "http://www.huaguoshan.com",
    "depends" : [
        'base',
        'odoo_eshop_base',
        ],
    'data': [
        'wizard/import_china_address_wizard_view.xml',
    ],
    "installable" : True,                 
    "active": True,       
    "category":'Generic Modules/Others' ,
    'description' : """
Import Chinese Address (province, city, district)
==================================================

Main Features
-------------
* import Chinese Address (province, city, district). 
* The source data are from http://www.stats.gov.cn/tjsj/tjbz/xzqhdm/201401/t20140116_501070.html
""",
}
