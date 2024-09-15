from sqlmodel import Field, SQLModel


class Lamp(SQLModel, table=True):
    id: str = Field(
        primary_key=True,
        description="Bezeichnung, Beispiel: XBO 10000 W/HS OFR",
    )

    title: str = Field(description="Titel, Beispiel: XBO 10000 W/HS OFR")

    applications: str = Field(
        description="Anwendungsgebiete, Beispiel: Klassische 35-mm-Filmprojektion..."
    )

    product_family_advantages: str = Field(
        description="Produktfamilien-Vorteile, Beispiel: Kurzbogen mit sehr hoher Leuchtdichte..."
    )

    product_family_characteristics: str = Field(
        description="Produktfamilien-Eigenschaften, Beispiel: Farbtemperatur: ca. 6.000 K..."
    )

    rated_power: float = Field(description="Nennleistung, Beispiel: 10000.00 W")
    rated_voltage: float = Field(description="Nennspannung, Beispiel: 50.0 V")
    rated_current: float = Field(description="Nennstrom, Beispiel: 195.00 A")
    current_control_range_min: float = Field(
        description="Stromsteuerbereich min., Beispiel: (160)…200 A"
    )

    current_control_range_max: float = Field(
        description="Stromsteuerbereich max., Beispiel: 160…(200) A"
    )

    diameter: float = Field(description="Durchmesser, Beispiel: 90.0 mm")
    length: float = Field(description="Länge, Beispiel: 436.0 mm")
    length_with_base_without_pin: float = Field(
        description="Länge mit Sockel jedoch ohne Sockelstift, Beispiel: 393.00 mm"
    )
    light_center_length: float = Field(
        description="Lichtschwerpunkt-Abstand (LCL), Beispiel: 170.5 mm"
    )
    electrode_distance_cold: float = Field(
        description="Elektrodenabstand kalt, Beispiel: 13.5 mm"
    )
    product_weight: float = Field(description="Produktgewicht, Beispiel: 1030.00 g")
    cable_length: float = Field(description="Kabellänge, Beispiel: 400.0 mm")

    max_ambient_temp_pinch: float = Field(
        description="Max. zulässige Umgebungstemperatur (Quetschung), Beispiel: 230 °C"
    )

    lifetime: float = Field(description="Lebensdauer, Beispiel: 300 Stunden")
    service_warranty_lifetime: float = Field(
        description="Servicegarantie-Lebensdauer, Beispiel: 400 Stunden"
    )

    base_anode: str = Field(description="Sockel Anode: Normbezeichnung")
    base_cathode: str = Field(description="Sockel Kathode: Normbezeichnung")
    product_note: str = Field(description="Produktanmerkung")

    cooling: str = Field(description="Kühlung, Beispiel: Forciert")
    burning_position: str = Field(description="Brennstellung, Beispiel: s15/p15")

    reach_date_of_declaration: str = Field(
        description="Datum der Deklaration, Beispiel: 18-08-2023"
    )
    reach_primary_product_numbers: str = Field(
        description="Primäre Erzeugnisnummer, Beispiel: 4050300624532 | 4008321552327 | 4062172030724"
    )
    reach_candidate_list_substance: str = Field(
        description="Stoff der Kandidatenliste 1, Beispiel: Blei"
    )
    reach_cas_number: str = Field(
        description="CAS Nr. des Stoffes 1, Beispiel: 7439-92-1"
    )
    reach_scip_declaration_number: str = Field(
        description="SCIP Deklarationsnummer, Beispiel: 7934C4E7-AD5D-4E20-9BAA-2349E600F6AD | cb26f713-f336-4c5c-b8f4-f0f8d52a0f47"
    )

    packaging_product_code: str = Field(
        description="Verpackungscode, Beispiel: 4062172030724"
    )
    packaging_unit: int = Field(
        description="Verpackungseinheit (Stück pro Einheit), Beispiel: 1"
    )
    packaging_length: float = Field(description="Verpackungslänge, Beispiel: 590 mm")
    packaging_width: float = Field(description="Verpackungsbreite, Beispiel: 234 mm")
    packaging_height: float = Field(description="Verpackungshöhe, Beispiel: 234 mm")
    packaging_volume: float = Field(
        description="Verpackungsvolumen, Beispiel: 32.31 dm³"
    )
    packaging_weight: float = Field(description="Bruttogewicht, Beispiel: 2179.00 g")
