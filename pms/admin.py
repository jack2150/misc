from django.contrib import admin
from pms.models import Position, InstrumentPos, StockPos, OptionPos, Option

admin.site.register(Position)
admin.site.register(InstrumentPos)
admin.site.register(StockPos)
admin.site.register(OptionPos)
admin.site.register(Option)