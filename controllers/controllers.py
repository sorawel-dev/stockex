# -*- coding: utf-8 -*-
# from odoo import http


# class Stockex(http.Controller):
#     @http.route('/stockex/stockex', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stockex/stockex/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('stockex.listing', {
#             'root': '/stockex/stockex',
#             'objects': http.request.env['stockex.stockex'].search([]),
#         })

#     @http.route('/stockex/stockex/objects/<model("stockex.stockex"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stockex.object', {
#             'object': obj
#         })

