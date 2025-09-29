from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsField,
    QgsGeometry,
    QgsVectorFileWriter,
    QgsWkbTypes,
    edit
)
from PyQt5.QtCore import QVariant

# 1. Qatlamni olish
layers = QgsProject.instance().mapLayersByName('Rezervuarlar')
if not layers:
    raise Exception("❌ 'Rezervuarlar' nomli qatlam topilmadi. Qatlam nomini tekshiring!")
layer = layers[0]

# 2. Yangi atribut ustunlari qo‘shish (agar mavjud bo‘lmasa)
provider = layer.dataProvider()
fields = layer.fields().names()

if 'rez_may' not in fields:
    provider.addAttributes([QgsField('rez_may', QVariant.Double)])
if 'rez_tur' not in fields:
    provider.addAttributes([QgsField('rez_tur', QVariant.String)])
layer.updateFields()

# 3. Yangi shapefile yaratiladigan joy
out_path = "D:/rezervuar_buffer.shp"   # <-- o'zingiznikiga moslang

# Yangi qatlam uchun fields (atributlar + geometriya)
out_fields = layer.fields()

_writer = QgsVectorFileWriter(out_path, 'UTF-8', out_fields,
                              QgsWkbTypes.Polygon, layer.crs(), 'ESRI Shapefile')

# 4. Har bir obyekt uchun shartlarni tekshirish va buffer yaratish
with edit(layer):
    for feat in layer.getFeatures():
        rez_holat = feat['rez_holat']

        if rez_holat == "yer osti":
            rez_may = 25
            rez_tur = None
        else:  # yer usti
            V = feat['V']
            if V < 20000:
                rez_tur = "B"
                rez_may = 40
            else:
                rez_tur = "A"
                rez_may = 50

        # Atributlarni yangilash
        fid = feat.id()
        layer.changeAttributeValue(fid, layer.fields().indexFromName('rez_may'), rez_may)
        if rez_tur:
            layer.changeAttributeValue(fid, layer.fields().indexFromName('rez_tur'), rez_tur)

        # Buffer yaratish
        geom = feat.geometry()
        if geom is None or geom.isEmpty():
            continue  # agar geometriya bo'sh bo'lsa, tashlab ketamiz

        buffer_geom = geom.buffer(rez_may, 30)  # 30 segment — silliqlik
        if buffer_geom.isEmpty():
            continue

        new_feat = QgsFeature(out_fields)
        new_feat.setGeometry(buffer_geom)
        new_feat.setAttributes(feat.attributes())
        _writer.addFeature(new_feat)

del _writer  # yozishni tugatish

print("✅ Ish yakunlandi. Natija fayl:", out_path)
