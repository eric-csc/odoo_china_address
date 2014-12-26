# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from lxml import etree
import  base64 

class import_china_address(osv.osv_memory):
    _name = "hgs.import_china_address"
    
    _columns = {
        'xml': fields.binary('xml文件', filters='*.xml'),  
    }
    
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = {}
        return res
    
    def import_china_address_from_xml(self, cr, uid, ids, context=None):  
        country_dict = {}
        province_dict = {}
        city_dict = {}
        district_dict = {}
        for wiz in self.browse(cr,uid,ids):  
            if not wiz.xml: 
                continue  
            try:
                xml_data = etree.fromstring( base64.decodestring(wiz.xml) )    
                area_Paramter = xml_data.find("areas").findall("area") 
                for area in area_Paramter:  
                    if area.find('type').text == 1 or area.find('type').text == '1':
                        if area.find('name').text == '中国' :
                            country = {}
                            country['name'] = area.find('name').text
                            country['id'] = area.find('id').text
                            country_dict['id'] = country
                    if area.find('type').text == 2 or area.find('type').text == '2':
                        province = {}
                        province['name'] = area.find('name').text
                        province['parent_id'] = area.find('parent_id').text
                        province['zip'] = area.find('zip').text
                        province_dict[area.find('id').text] = province
                    if area.find('type').text == 3 or area.find('type').text == '3':
                        city = {}
                        city['name'] = area.find('name').text
                        city['parent_id'] = area.find('parent_id').text
                        city['zip'] = area.find('zip').text
                        city_dict[area.find('id').text] = city
                    if area.find('type').text == 4 or area.find('type').text == '4':
                        district = {}
                        district['name'] = area.find('name').text
                        district['parent_id'] = area.find('parent_id').text
                        district['zip'] = area.find('zip').text
                        district_dict[area.find('id').text] = district
            except Exception,e:
                msg = u'解析数据异常:%s',str(e)
                return msg
        self.import_country(cr,uid,country_dict)
        self.import_province(cr,uid,country_dict, province_dict)
        self.import_city(cr,uid,country_dict,province_dict, city_dict)
        self.import_district(cr,uid,country_dict,province_dict, city_dict,district_dict)
            
    def import_country(self,cr,uid,country_dict):
        country_obj = self.pool.get('res.country')
        ids = country_obj.search(cr, uid, ['|',('name','=', ('China')),('name','=', ('中国'))])
        if not ids:
            vals = {
                 'name': 'China', 'Code': 'CH'
                 }
            ids = country_obj.create(cr, uid, vals)
            country_dict['orm_id'] = ids
        else:
            if len(ids) > 1:
                raise osv.except_osv(_('Warning!'), _(u'只能有一个中国！')) 
            country_dict['orm_id'] = ids[0]
    
    def import_province(self,cr,uid,country_dict, province_dict):
        for province_id in province_dict.keys():
            vals = {
                        'name': province_dict[province_id]['name'],
                        'country_id':country_dict['orm_id'],
                        'code':'cod'
                }
            province_ids = self.pool.get('res.country.state').search(cr, uid, [('name','=',vals['name'] )])
            if not province_ids:
                province_dict[province_id]['orm_id'] = self.pool.get('res.country.state').create(cr,uid,vals)
            else:
                if len(province_ids) > 1:
                    raise osv.except_osv(_('Warning!'), _(u'只能有一个%s！',province_dict[province_id]['name'] ))
                self.pool.get('res.country.state').write(cr, uid, province_ids, vals)
                province_dict[province_id]['orm_id'] = province_ids[0]
    
    def import_city(self,cr,uid,country_dict,province_dict, city_dict):
        for city_id in city_dict.keys():
            vals = {
                        'name': city_dict[city_id]['name'],
                        'country_id':country_dict['orm_id'],
                        'state_id':province_dict[city_dict[city_id]['parent_id']]['orm_id'],
                        'code':'cod'
                }
            city_ids = self.pool.get('res.country.state.city').search(cr, uid, ['&',('state_id','=', vals['state_id']),
                                                                                       ('name','=',vals['name'] )] )
            if not city_ids:
                city_dict[city_id]['orm_id'] = self.pool.get('res.country.state.city').create(cr,uid,vals)
            else:
                if len(city_ids) > 1:
                    raise osv.except_osv(_('Warning!'), _(u'只能有一个%s！',city_dict[city_id]['name'] )) 
                self.pool.get('res.country.state.city').write(cr, uid, city_ids, vals)
                city_dict[city_id]['orm_id'] = city_ids[0]
    
    def import_district(self,cr,uid,country_dict,province_dict, city_dict,district_dict):
        for district_id in district_dict.keys():
            try:
                city_id = district_dict[district_id]['parent_id']
                city_orm_id = city_dict[city_id]['orm_id']
                province_id = city_dict[ district_dict[district_id]['parent_id']]['parent_id']
                province_orm_id = province_dict[province_id]['orm_id']
                vals = {
                        'name': district_dict[district_id]['name'],
                        'country_id':country_dict['orm_id'],
                        'state_id':province_orm_id,
                        'city_id':city_orm_id,
                        'code':'cod'
                }
                district_ids = self.pool.get('res.country.state.city.district').search(cr, uid, ['&',('city_id','=', vals['city_id']),
                                                                                   ('name','=',vals['name'] )] )
                if not district_ids:
                    self.pool.get('res.country.state.city.district').create(cr,uid,vals)
                else:
                    if len(district_ids) > 1:
                        raise osv.except_osv(_('Warning!'), _(u'只能有一个%s！',district_dict[district_id]['name'] ))
                    self.pool.get('res.country.state.city.district').write(cr, uid, district_ids, vals)
            except Exception,e:
                self.import_district_as_city(cr,uid,country_dict,province_dict, city_dict,district_dict, district_id) 
    
    def import_district_as_city(self,cr,uid,country_dict,province_dict, city_dict,district_dict, district_id):
        '''一些县级市直接归省管辖
        '''
        try:
            province_id =  district_dict[district_id]['parent_id']
            province_orm_id = province_dict[province_id]['orm_id']
            vals = {
                        'name': district_dict[district_id]['name'],
                        'country_id':country_dict['orm_id'],
                        'state_id':province_orm_id,
                        'code':'cod'
                }
            city_ids = self.pool.get('res.country.state.city').search(cr, uid, ['&',('state_id','=', vals['state_id']),
                                                                                   ('name','=',vals['name'] )] )
            if not city_ids:
                    self.pool.get('res.country.state.city').create(cr,uid,vals)
            else:
                    if len(city_ids) > 1:
                        raise osv.except_osv(_('Warning!'), _(u'只能有一个%s！',district_dict[district_id]['name'] ))
                    self.pool.get('res.country.state.city').write(cr, uid, city_ids, vals)
        except Exception,e:
            pass
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
