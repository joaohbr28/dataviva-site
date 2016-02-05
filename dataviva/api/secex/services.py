from dataviva.api.attrs.models import Bra, Hs, Wld
from dataviva.api.secex.models import Ymw, Ymbw, Ympw, Ymp, Ymbp, Ymbpw
from dataviva import db
from flask import g
from sqlalchemy.sql.expression import func, desc, asc

class TradePartner:
    def __init__(self, wld_id):
        self._secex = None
        self._secex_sorted_by_balance = None
        self._secex_sorted_by_exports = None
        self._secex_sorted_by_imports = None
        self.wld_id = wld_id
        self.max_year_query = db.session.query(func.max(Ymw.year)).filter_by(wld_id=wld_id)
        self.secex_query = Ymw.query.join(Wld).filter(
            Ymw.wld_id == self.wld_id,
            Ymw.month == 0,
            Ymw.year == self.max_year_query)

    def __secex__(self):
        if not self._secex:
            secex_data = self.secex_query.first_or_404()
            self._secex = secex_data
        return self._secex

    def __secex_list__(self):
        if not self._secex:
            secex_data = self.secex_query.all()
            self._secex = secex_data
        return self._secex

    def __secex_sorted_by_balance__(self):
        self._secex_sorted_by_balance = self.__secex_list__()
        self._secex_sorted_by_balance.sort(key=lambda secex: (secex.export_val or 0) - (secex.import_val or 0), reverse=True)
        return self._secex_sorted_by_balance

    def __secex_sorted_by_exports__(self):
        self._secex_sorted_by_exports = self.__secex_list__()
        self._secex_sorted_by_exports.sort(key=lambda secex: secex.export_val, reverse=True)
        return self._secex_sorted_by_exports

    def __secex_sorted_by_imports__(self):
        self._secex_sorted_by_imports = self.__secex_list__()
        self._secex_sorted_by_imports.sort(key=lambda secex: secex.import_val, reverse=True)
        return self._secex_sorted_by_imports

    def country_name(self):
        base_trade_partner = self.__secex__().wld
        return base_trade_partner.name()

    def year(self):
        return self.__secex__().year

    def trade_balance(self):
        export_val = self.__secex__().export_val
        import_val = self.__secex__().import_val
        return export_val - import_val

    def total_exported(self):
        return self.__secex__().export_val

    def unity_weight_export_price(self):
        export_val = self.__secex__().export_val
        export_kg = self.__secex__().export_kg
        return export_val / export_kg

    def total_imported(self):
        return self.__secex__().import_val

    def unity_weight_import_price(self):
        import_val = self.__secex__().import_val
        import_kg = self.__secex__().import_kg
        return import_val / import_kg

    def highest_import_value(self):
        secex = self.__secex_sorted_by_imports__()[0]
        return secex.import_val

    def highest_export_value(self):
        secex = self.__secex_sorted_by_exports__()[0]
        return secex.export_val

    def highest_balance(self):
        secex = self.__secex_sorted_by_balance__()[0]
        export_val = secex.export_val or 0
        import_val = secex.import_val or 0
        return export_val - import_val

    def lowest_balance(self):
        secex = self.__secex_sorted_by_balance__()[-1]
        export_val = secex.export_val or 0
        import_val = secex.import_val or 0
        return export_val - import_val


class TradePartnerMunicipalities(TradePartner):
    def __init__(self, wld_id):
        TradePartner.__init__(self, wld_id)
        self.max_year_query = db.session.query(func.max(Ymbw.year)).filter_by(wld_id=wld_id)
        self.secex_query = Ymbw.query.join(Wld).join(Bra).filter(
            Ymbw.wld_id == self.wld_id,
            Ymbw.month == 0,
            Ymbw.year == self.max_year_query,
            func.length(Ymbw.bra_id) == 9)

    def municipality_with_more_imports(self):
        secex = self.__secex_sorted_by_imports__()[0]
        return secex.bra.name()

    def municipality_with_more_exports(self):
        secex = self.__secex_sorted_by_exports__()[0]
        return secex.bra.name()


class TradePartnerProducts(TradePartner):
    def __init__(self, wld_id):
        TradePartner.__init__(self, wld_id)
        self.max_year_query = db.session.query(func.max(Ympw.year)).filter_by(wld_id=wld_id)
        self.secex_query = Ympw.query.join(Wld).join(Hs).filter(
            Ympw.wld_id == self.wld_id,
            Ympw.month == 0,
            Ympw.hs_id_len == 6,
            Ympw.year == self.max_year_query)

    def product_with_more_exports(self):
        secex = self.__secex_sorted_by_exports__()[0]
        return secex.hs.name()

    def product_with_more_imports(self):
        secex = self.__secex_sorted_by_imports__()[0]
        return secex.hs.name()

    def product_with_highest_balance(self):
        secex = self.__secex_sorted_by_balance__()[0]
        return secex.hs.name()

    def product_with_lowest_balance(self):
        secex = self.__secex_sorted_by_balance__()[-1]
        return secex.hs.name()

class Product:
    def __init__(self, product_id):
        self._secex = None
        self._secex_sorted_by_balance = None
        self._secex_sorted_by_exports = None
        self._secex_sorted_by_imports = None
        self.product_id = product_id
        self.max_year_query = db.session.query(func.max(Ymp.year)).filter_by(hs_id=product_id)
        self.secex_query= Ymp.query.join(Hs).filter(
            Ymp.hs_id==self.product_id,
            Ymp.month==0,
            Ymp.year==self.max_year_query)

    def __secex__(self):
        if not self._secex:
            secex_data = self.secex_query.first_or_404()
            self._secex = secex_data
        return self._secex

    def __secex_list__(self):
        if not self._secex:
            secex_data = self.secex_query.all()
            self._secex = secex_data
        return self._secex

    def __secex_sorted_by_balance__(self):
        self._secex_sorted_by_balance = self.__secex_list__()
        self._secex_sorted_by_balance.sort(key=lambda secex: (secex.export_val or 0) - (secex.import_val or 0), reverse=True)
        return self._secex_sorted_by_balance

    def __secex_sorted_by_exports__(self):
        self._secex_sorted_by_exports = self.__secex_list__()
        self._secex_sorted_by_exports.sort(key=lambda secex: secex.export_val, reverse=True)
        return self._secex_sorted_by_exports

    def __secex_sorted_by_imports__(self):
        self._secex_sorted_by_imports = self.__secex_list__()
        self._secex_sorted_by_imports.sort(key=lambda secex: secex.import_val, reverse=True)
        return self._secex_sorted_by_imports

    def product_name(self):
        product = self.__secex__().hs
        return product.name()

    def year(self):
        return self.__secex__().year

    def trade_balance(self):
        export_val = self.__secex__().export_val
        import_val = self.__secex__().import_val
        return export_val - import_val

    def total_exported(self):
        return self.__secex__().export_val

    def unity_weight_export_price(self):
        export_val = self.__secex__().export_val
        export_kg = self.__secex__().export_kg
        return export_val / export_kg

    def total_imported(self):
        return self.__secex__().import_val

    def unity_weight_import_price(self):
        import_val = self.__secex__().import_val
        import_kg = self.__secex__().import_kg
        return import_val / import_kg

    def highest_import_value(self):
        secex = self.__secex_sorted_by_imports__()[0]
        return secex.import_val

    def highest_export_value(self):
        secex = self.__secex_sorted_by_exports__()[0]
        return secex.export_val

    def highest_balance(self):
        secex = self.__secex_sorted_by_balance__()[0]
        export_val = secex.export_val or 0
        import_val = secex.import_val or 0
        return export_val - import_val

    def lowest_balance(self):
        secex = self.__secex_sorted_by_balance__()[-1]
        export_val = secex.export_val or 0
        import_val = secex.import_val or 0
        return export_val - import_val

    def product_complexity(self):
        product_complexity = self.__secex__().pci()
        return product_complexity


class ProductTradePartners(Product):
    def __init__(self, product_id):
        Product.__init__(self, product_id)
        self.max_year_query = db.session.query(func.max(Ympw.year)).filter_by(hs_id=product_id)
        ympw_query = Ympw.query.join(Wld).filter(
            Ympw.hs_id==self.product_id,
            Ympw.wld_id_len==5,
            Ympw.month==0,
            Ympw.year==self.max_year_query
        )

        secex = ympw_query.one()
        return secex

    def destination_with_more_exports(self):
        secex = self.__secex_sorted_by_exports__()[0]
        return secex.wld.name()

    def highest_export_value(self):
        secex = self.highest_export_value()[0]
        return secex.export_val

    def origin_with_more_imports(self):
        secex = self.__secex_sorted_by_imports__()[0]
        return secex.wld.name()

    def highest_import_value(self):
        secex = self.highest_import_value()[0]
        return secex.import_val


class ProductMunicipalities(Product):
    def __init__(self, product_id):
        Product.__init__(self, product_id)
        self.ymax_year_query = db.session.query(func.max(Ymbp.year)).filter_by(hs_id=product_id)
        ymbp_query = Ymbp.query.join(Bra).filter(
            Ymbp.hs_id==self.product_id,
            Ymbp.bra_id_len==9,
            Ymbp.month==0,
            Ymbp.year==self.max_year_query,
        )

        secex = ymbp_query.one()
        return secex

    def municipality_with_more_exports(self):
        secex = self.__secex_sorted_by_exports__()[0]
        return secex.bra.name()

    def highest_export_value_by_municipality(self):
        secex = self.__secex_sorted_by_exports__()[0]
        return secex.export_val

    def municipality_with_more_imports(self):
        secex = self.__secex_sorted_by_imports__()[0]
        return secex.bra.name()

    def highest_import_value_by_municipality(self):
        secex = self.__secex_sorted_by_imports__()[0]
        return secex.import_val


class ProductLocations(Product):
    def __init__(self, bra_id,  product_id):
        self._secex = None
        self.bra_id = bra_id
        self.product_id = product_id
        self.max_year_query = db.session.query(func.max(Ymbp.year)).filter_by(hs_id=product_id)
        ymbp_query = Ymbp.query.join(Bra).filter(
            Ymbp.hs_id==self.product_id,
            Ymbp.bra_id_len==9,
            Ymbp.bra_id.like(str(self.bra_id)+'%'),
            Ymbp.month==0,
            Ymbp.year==self.max_year_query)

        secex = ymbp_query.one()
        return secex

    def rca_wld(self):
        secex = self.__secex__()
        return secex.rca_wld

    def distance_wld(self):
        secex = self.__secex__()
        return secex.distance_wld

    def opp_gain_wld(self):
        secex = self.__secex__()
        return secex.opp_gain_wld


class ProductLocationsTradePartners(ProductLocations):
    def __init__(self, product_id):
        ProductLocations.__init__(self, product_id)
        self.max_year_query = db.session.query(func.max(Ymbpw.year)).filter_by(hs_id=product_id, bra_id=bra_id)
        ymbpw_query = Ymbpw.query.join(Wld).filter(
            Ymbpw.hs_id==self.product_id,
            Ymbpw.year==self.ymbpw_max_year_query,
            Ymbpw.wld_id_len==5,
            Ymbpw.bra_id.like(str(self.bra_id)+'%'),
            Ymbpw.month==0)

        secex = ymbpw_query.one()
        return secex

    def destination_with_more_exports(self):
        secex = self.__secex_sorted_by_exports__()[0]
        return secex.wld.name()

    def highest_export_value_by_destination(self):
        secex = self.__secex_sorted_by_exports__()[0]
        return secex.export_val

    def origin_with_more_imports(self):
        secex = self.__secex_sorted_by_imports__()[0]
        return secex.bra.name()

    def highest_import_value_by_origin(self):
        secex = self.__secex_sorted_by_imports__()[0]
        return secex.import_val


class ProductLocationsMunicipalities(ProductLocations):
    def __init__(self, product_id):
        ProductLocations.__init__(self, product_id)
        self.ymbp_max_year_query = db.session.query(func.max(Ymbp.year)).filter_by(hs_id=product_id)
        ymbp_query = Ymbp.query.join(Bra).filter(
            Ymbp.hs_id==self.product_id,
            Ymbp.year==self.ymbp_max_year_query,
            Ymbp.bra_id_len==9,
            Ymbp.bra_id.like(str(self.bra_id)+'%'),
            Ymbp.month==0)

        secex = ymbp_query.one()
        return secex

    def municipality_with_more_exports(self):
        secex = self.__secex_sorted_by_exports__()[0]
        return secex.bra.name()

    def highest_export_value_by_municipality(self):
        secex = self.__secex_sorted_by_exports__()[0]
        return secex.export_val

    def municipality_with_more_imports(self):
        secex = self.__secex_sorted_by_imports__()[0]
        return secex.bra.name()

    def highest_import_value_by_municipality(self):
        secex = self.__secex_sorted_by_imports__()[0]
        return secex.import_val















