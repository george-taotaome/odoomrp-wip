# -*- encoding: utf-8 -*-
##############################################################################
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
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
from openerp import models, fields


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    manual_production_lot = fields.Char(string='Manual Production Lot')
    concatenate_lots_components = fields.Boolean(
        string='Concatenate Lots Components')

    def action_produce(self, cr, uid, production_id, production_qty,
                       production_mode, wiz=False, context=None):
        lot_obj = self.pool['stock.production.lot']
        product_produce_obj = self.pool['mrp.product.produce']
        if production_mode == 'consume_produce' and wiz:
            production = self.browse(cr, uid, production_id, context=context)
            if (production.product_id.track_all or
                production.product_id.track_production or
                    production.product_id.track_incoming):
                lot_id = False
                for line in production.move_created_ids2:
                    if (line.product_id.id == production.product_id.id and
                            line.restrict_lot_id):
                        lot_id = line.restric_lot_id.id
                        break
                if not lot_id:
                    code = ("%s%s" %
                            (production.manual_production_lot or '',
                             production.name))
                    if production.concatenate_lots_components:
                        lot_ids = set()
                        for line in wiz.consume_lines:
                            if line.lot_id:
                                lot_ids.add(line.lot_id.id)
                        for line in production.move_lines2:
                            if line.restrict_lot_id:
                                lot_ids.add(line.restrict_lot_id.id)
                        for lot in lot_obj.browse(cr, uid, lot_ids,
                                                  context=context):
                            code += '-%s' % lot.name
                    vals = {'name': code,
                            'product_id': production.product_id.id}
                    lot_id = lot_obj.create(cr, uid, vals, context=context)
                vals = {'lot_id': lot_id}
                product_produce_obj.write(cr, uid, wiz.id, vals,
                                          context=context)
        return super(MrpProduction, self).action_produce(
            cr, uid, production_id, production_qty, production_mode, wiz=wiz,
            context=context)
