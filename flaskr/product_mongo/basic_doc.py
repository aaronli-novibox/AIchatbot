from mongoengine import Document, EnumField, EmailField, DecimalField, StringField, URLField, BooleanField, DateTimeField, FloatField, IntField, EmbeddedDocument, EmbeddedDocumentField, ListField, LazyReferenceField
from enum import Enum
from datetime import datetime
# from mongo_doc import *
# fmt: off


class Image(EmbeddedDocument):
    url = URLField()


class CurrencyCode(Enum):
    AED = "AED"
    AFN = "AFN"
    ALL = "ALL"
    AMD = "AMD"
    ANG = "ANG"
    AOA = "AOA"
    ARS = "ARS"
    AUD = "AUD"
    AWG = "AWG"
    AZN = "AZN"
    BAM = "BAM"
    BBD = "BBD"
    BDT = "BDT"
    BGN = "BGN"
    BHD = "BHD"
    BIF = "BIF"
    BMD = "BMD"
    BND = "BND"
    BOB = "BOB"
    BRL = "BRL"
    BSD = "BSD"
    BTN = "BTN"
    BWP = "BWP"
    BYN = "BYN"
    BZD = "BZD"
    CAD = "CAD"
    CDF = "CDF"
    CHF = "CHF"
    CLP = "CLP"
    CNY = "CNY"
    COP = "COP"
    CRC = "CRC"
    CVE = "CVE"
    CZK = "CZK"
    DJF = "DJF"
    DKK = "DKK"
    DOP = "DOP"
    DZD = "DZD"
    EGP = "EGP"
    ERN = "ERN"
    ETB = "ETB"
    EUR = "EUR"
    FJD = "FJD"
    FKP = "FKP"
    GBP = "GBP"
    GEL = "GEL"
    GHS = "GHS"
    GIP = "GIP"
    GMD = "GMD"
    GNF = "GNF"
    GTQ = "GTQ"
    GYD = "GYD"
    HKD = "HKD"
    HNL = "HNL"
    HRK = "HRK"
    HTG = "HTG"
    HUF = "HUF"
    IDR = "IDR"
    ILS = "ILS"
    INR = "INR"
    IQD = "IQD"
    IRR = "IRR"
    ISK = "ISK"
    JEP = "JEP"
    JMD = "JMD"
    JOD = "JOD"
    JPY = "JPY"
    KES = "KES"
    KGS = "KGS"
    KHR = "KHR"
    KID = "KID"
    KMF = "KMF"
    KRW = "KRW"
    KWD = "KWD"
    KYD = "KYD"
    KZT = "KZT"
    LAK = "LAK"
    LBP = "LBP"
    LKR = "LKR"
    LRD = "LRD"
    LSL = "LSL"
    LTL = "LTL"
    LVL = "LVL"
    LYD = "LYD"
    MAD = "MAD"
    MDL = "MDL"
    MGA = "MGA"
    MKD = "MKD"
    MMK = "MMK"
    MNT = "MNT"
    MOP = "MOP"
    MRU = "MRU"
    MUR = "MUR"
    MVR = "MVR"
    MWK = "MWK"
    MXN = "MXN"
    MYR = "MYR"
    MZN = "MZN"
    NAD = "NAD"
    NGN = "NGN"
    NIO = "NIO"
    NOK = "NOK"
    NPR = "NPR"
    NZD = "NZD"
    OMR = "OMR"
    PAB = "PAB"
    PEN = "PEN"
    PGK = "PGK"
    PHP = "PHP"
    PKR = "PKR"
    PLN = "PLN"
    PYG = "PYG"
    QAR = "QAR"
    RON = "RON"
    RSD = "RSD"
    RUB = "RUB"
    RWF = "RWF"
    SAR = "SAR"
    SBD = "SBD"
    SCR = "SCR"
    SDG = "SDG"
    SEK = "SEK"
    SGD = "SGD"
    SHP = "SHP"
    SLL = "SLL"
    SOS = "SOS"
    SRD = "SRD"
    SSP = "SSP"
    STN = "STN"
    SYP = "SYP"
    SZL = "SZL"
    THB = "THB"
    TJS = "TJS"
    TMT = "TMT"
    TND = "TND"
    TOP = "TOP"
    TRY = "TRY"
    TTD = "TTD"
    TWD = "TWD"
    TZS = "TZS"
    UAH = "UAH"
    UGX = "UGX"
    USD = "USD"
    UYU = "UYU"
    UZS = "UZS"
    VED = "VED"
    VES = "VES"
    VND = "VND"
    VUV = "VUV"
    WST = "WST"
    XAF = "XAF"
    XCD = "XCD"
    XOF = "XOF"
    XPF = "XPF"
    XXX = "XXX"
    YER = "YER"
    ZAR = "ZAR"
    ZMW = "ZMW"
    BYR = "BYR"
    STD = "STD"
    VEF = "VEF"



class MoneyV2(EmbeddedDocument):
    amount = DecimalField(required=True,
                          precision=2,
                          help_text="Decimal money amount.")
    currencyCode = StringField(required=True,
                               choices=[code.name for code in CurrencyCode],
                               help_text="Currency of the money.")


class MoneyBag(EmbeddedDocument):
    presentmentMoney = EmbeddedDocumentField(MoneyV2, required=True, help_text="Amount in presentment currency.")
    shopMoney = EmbeddedDocumentField(MoneyV2, required=True, help_text="Amount in shop currency.")

class PriceRangeV2(EmbeddedDocument):
    maxVariantPrice = EmbeddedDocumentField(
        MoneyV2, required=True, help_text="The highest variant's price.")
    minVariantPrice = EmbeddedDocumentField(
        MoneyV2, required=True, help_text="The lowest variant's price.")


class InventoryQuantity(Document):
    shopify_id = StringField(unique=True, required=True)
    name = StringField(required=True)
    quantity = IntField(required=True)
    updatedAt = DateTimeField(default=datetime.now)

class Metafield(Document):

    shopify_id = StringField(required=True, unique=True, help_text="Globally unique identifier.")
    namespace = StringField(required=True, help_text="The container for a set of metadata.")
    key = StringField(required=True, help_text="A unique identifier for the metafield.")
    value = StringField(required=True, help_text="Information to be stored as metadata.")


class ProductOption(Document):
    shopify_id = StringField(required=True, unique=True, help_text="Globally unique identifier.")
    position = IntField()
    name = StringField()
    values = ListField(StringField())

class LocationAddress(EmbeddedDocument):
    address1 = StringField(help_text="The first line of the address for the location.")
    address2 = StringField(help_text="The second line of the address for the location.")
    city = StringField(help_text="The city of the location.")
    country = StringField(help_text="The country of the location.")
    countryCode = StringField(help_text="The country code of the location.")
    formatted = ListField(StringField(), required=True, help_text="A formatted version of the address for the location.")
    latitude = FloatField(help_text="The approximate latitude coordinates of the location.")
    longitude = FloatField(help_text="The approximate longitude coordinates of the location.")
    phone = StringField(help_text="The phone number of the location.")
    province = StringField(help_text="The province of the location.")
    provinceCode = StringField(help_text="The code for the province, state, or district of the address of the location.")
    zip = StringField(help_text="The ZIP code of the location.")

class TaxLine(EmbeddedDocument):
    channelLiable = BooleanField()
    priceSet = EmbeddedDocumentField(MoneyBag, required=True)
    rate = FloatField()
    ratePercentage = FloatField()
    title = StringField(required=True)
    # price = EmbeddedDocumentField(Money, required=True)


class DeliveryLocalPickupTime(Enum):
    FIVE_OR_MORE_DAYS = 'FIVE_OR_MORE_DAYS'
    FOUR_HOURS = 'FOUR_HOURS'
    ONE_HOUR = 'ONE_HOUR'
    TWENTY_FOUR_HOURS = 'TWENTY_FOUR_HOURS'
    TWO_HOURS = 'TWO_HOURS'
    TWO_TO_FOUR_DAYS = 'TWO_TO_FOUR_DAYS'


class DeliveryLocalPickupSettings(EmbeddedDocument):

    instructions = StringField(help_text="Additional instructions or information related to the local pickup.")
    pickupTime = EnumField(DeliveryLocalPickupTime, required=True, help_text="The estimated pickup time to show customers at checkout.")


class LocationSuggestedAddress(EmbeddedDocument):
    address1 = StringField(help_text="The first line of the suggested address.")
    address2 = StringField(help_text="The second line of the suggested address.")
    city = StringField(help_text="The city of the suggested address.")
    country = StringField(help_text="The country of the suggested address.")
    countryCode = StringField(help_text="The country code of the suggested address.")
    formatted = ListField(StringField(), required=True, help_text="A formatted version of the suggested address.")
    province = StringField(help_text="The province of the suggested address.")
    provinceCode = StringField(help_text="The code for the province, state, or district of the suggested address.")
    zip = StringField(help_text="The ZIP code of the suggested address.")



class LineItem(Document):
    shopify_id = StringField(required=True, unique=True, help_text="Globally unique identifier.")
    lineitem_quantity = IntField(required=True, help_text="The number of items purchased.")
    lineitem_name = StringField(required=True, help_text="The title of the product.")
    lineitem_price = FloatField(required=True, help_text="The price of the item.")
    lineitem_compare_at_price = DecimalField(help_text="The compare at price of the item.")
    lineitem_sku = StringField(help_text="The SKU of the item.")
    lineitem_requires_shipping = BooleanField(help_text="Whether the item requires shipping.")
    lineitem_taxable = BooleanField(help_text="Whether the item is taxable.")
    lineitem_fulfillment_status = StringField(help_text="The fulfillment status of the item.")
    lineitem_discount = FloatField(help_text="The discount amount applied to the item.")
    vendor = StringField(help_text="The vendor of the item.")
    product = LazyReferenceField('Product')
    order = LazyReferenceField('Order')
    variant = LazyReferenceField('ProductVariant')
    commission_fee = FloatField(required=True, help_text="The commission fee = price*quantity*commission")
    commission = StringField(help_text='commission of commission fee')





class NavigationItem(Document):
    # Assuming a simplified structure; add more specific fields as necessary
    shopify_id = StringField(required=True, unique=True)
    title = StringField(required=True)
    url = URLField()




class CustomerAddress(EmbeddedDocument):
    shopify_id = StringField(required=True, unique=True, help_text="Globally-unique identifier for the address.")
    address1 = StringField(help_text="The first line of the address, typically the street address or PO Box number.")
    address2 = StringField(help_text="The second line of the address, often the apartment, suite, or unit number.")
    city = StringField(help_text="The name of the city, district, village, or town.")
    company = StringField(help_text="The name of the customer's company or organization, if applicable.")
    country = StringField(help_text="The name of the country.")
    firstName = StringField(help_text="The first name of the person associated with the address.")
    formattedArea = StringField(help_text="A comma-separated list of the values for city, province, and country.")
    lastName = StringField(help_text="The last name of the person associated with the address.")
    name = StringField(help_text="The full name of the person associated with the address.")
    phoneNumber = StringField(help_text="The phone number associated with the address, formatted to E.164 standard.")
    province = StringField(help_text="The province, state, or district of the address.")
    territoryCode = StringField(help_text="The two-letter country code for the country of the address.")
    zip = StringField(help_text="The postal or ZIP code of the address.")
    zoneCode = StringField(help_text="The two-letter code for the region, such as a state or province code.")




# orders
class DiscountApplicationAllocationMethod(Enum):
    ACROSS = 'ACROSS'
    EACH = 'EACH'
    ONE = 'ONE'

class DiscountApplicationTargetSelection(Enum):
    ALL = 'ALL'
    ENTITLED = 'ENTITLED'
    EXPLICIT = 'EXPLICIT'

class DiscountApplicationTargetType(Enum):
    LINE_ITEM = 'LINE_ITEM'
    SHIPPING_LINE = 'SHIPPING_LINE'


class PricingPercentageValue(EmbeddedDocument):
    percentage = FloatField(required=True, help_text="The percentage value of the discount application.")


class PricingValue(EmbeddedDocument):
    MoneyV2 = EmbeddedDocumentField(MoneyV2)
    PricingPercentageValue = EmbeddedDocumentField('PricingPercentageValue')


class DiscountApplication(EmbeddedDocument):
    allocationMethod = StringField(choices=[(method.value, method.name) for method in DiscountApplicationAllocationMethod], required=True, help_text="The method by which the discount's value is allocated to its entitled items.")
    targetSelection = StringField(choices=[(selection.value, selection.name) for selection in DiscountApplicationTargetSelection], required=True, help_text="The lines of targetType that the discount is allocated over.")
    targetType = StringField(choices=[(type.value, type.name) for type in DiscountApplicationTargetType], required=True, help_text="The type of line that the discount is applicable towards.")
    value = EmbeddedDocumentField(PricingValue, required=True, help_text="The value of the discount application.")


class DiscountAllocation(EmbeddedDocument):
    allocatedAmount = EmbeddedDocumentField(MoneyV2, required=True, help_text="The amount of discount allocated.")
    discountApplication = EmbeddedDocumentField(DiscountApplication, required=True, help_text="The discount application associated with the allocation.")


class OrderTransactionKind(Enum):
    AUTHORIZATION = 'AUTHORIZATION'
    CAPTURE = 'CAPTURE'
    CARD_APPROVAL = 'CARD_APPROVAL'
    CARD_DECLINE = 'CARD_DECLINE'
    CHANGE = 'CHANGE'
    EMV_AUTHORIZATION = 'EMV_AUTHORIZATION'
    REFUND = 'REFUND'
    REFUND_EMV_INITIATE = 'REFUND_EMV_INITIATE'
    SALE = 'SALE'
    SUGGESTED_REFUND = 'SUGGESTED_REFUND'
    VOID = 'VOID'

class GiftCardDetails(EmbeddedDocument):
    balance = EmbeddedDocumentField(MoneyV2, required=True, help_text="The balance of the gift card in shop and presentment currencies.")
    last4 = StringField(required=True, help_text="The last characters of the gift card.")



class DiscountApplicationAllocationMethod(Enum):
    ACROSS = 'ACROSS'
    EACH = 'EACH'
    ONE = 'ONE'

class DiscountApplicationTargetSelection(Enum):
    ALL = 'ALL'
    ENTITLED = 'ENTITLED'
    EXPLICIT = 'EXPLICIT'

class DiscountApplicationTargetType(Enum):
    LINE_ITEM = 'LINE_ITEM'
    SHIPPING_LINE = 'SHIPPING_LINE'

class PricingValue(EmbeddedDocument):
    MoneyV2 = EmbeddedDocumentField(MoneyV2)
    PricingPercentageValue = EmbeddedDocumentField('PricingPercentageValue')


class DiscountApplication(EmbeddedDocument):
    allocationMethod = StringField(choices=[(method.value, method.name) for method in DiscountApplicationAllocationMethod], required=True, help_text="The method by which the discount's value is allocated to its entitled items.")
    targetSelection = StringField(choices=[(selection.value, selection.name) for selection in DiscountApplicationTargetSelection], required=True, help_text="The lines of targetType that the discount is allocated over.")
    targetType = StringField(choices=[(type.value, type.name) for type in DiscountApplicationTargetType], required=True, help_text="The type of line that the discount is applicable towards.")
    value = EmbeddedDocumentField(PricingValue, required=True, help_text="The value of the discount application.")
    index = IntField(help_text="The index of the discount application as defined by the API.")


class DiscountAllocation(EmbeddedDocument):
    allocatedAmountSet = EmbeddedDocumentField('MoneyBag', required=True, help_text="The amount of discount allocated.")
    discountApplication = EmbeddedDocumentField('DiscountApplication', required=True, help_text="The discount application associated with the allocation.")
    # allocatedAmount = EmbeddedDocumentField(MoneyV2, required=True, help_text="The amount of discount allocated.")


class FulfillmentServiceType(Enum):
    GIFT_CARD = 'GIFT_CARD'
    MANUAL = 'MANUAL'
    THIRD_PARTY = 'THIRD_PARTY'




class FulfillmentService(Document):
    callbackUrl = URLField()
    handle = StringField()
    shopify_id = StringField(required=True, unique=True, help_text="Globally unique identifier.")
    inventoryManagement = BooleanField()
    location = LazyReferenceField('Location')
    permitsSkuSharing = BooleanField()
    productBased = BooleanField()
    serviceName = StringField()
    type = EnumField(FulfillmentServiceType)



class ShippingLine(Document):
    carrierIdentifier = StringField()
    code = StringField()
    custom = BooleanField()
    deliveryCategory = StringField()
    discountAllocations = ListField(EmbeddedDocumentField('DiscountAllocation'))
    discountedPriceSet = EmbeddedDocumentField('MoneyBag',required=True)
    shopify_id = StringField(required=True, unique=True, help_text="Globally unique identifier.")
    # isRemoved = BooleanField(required=True)
    originalPriceSet = EmbeddedDocumentField('MoneyBag',required=True)
    phone = StringField()
    requestedFulfillmentService = LazyReferenceField(FulfillmentService)
    shippingRateHandle = StringField()
    source = StringField()
    taxLines = ListField(EmbeddedDocumentField('TaxLine'))
    title = StringField(required=True)


class CardPaymentDetails(EmbeddedDocument):
    cardBrand = StringField(required=True, help_text="The brand of the credit card used.")
    last4 = StringField(help_text="The last four digits of the credit card used.")


class PaymentDetails(EmbeddedDocument):
    cardPaymentDetails = EmbeddedDocumentField(CardPaymentDetails)





class OrderTransactionType(Enum):
    BANK_DEPOSIT = 'BANK_DEPOSIT'
    CARD = 'CARD'
    CASH_ON_DELIVERY = 'CASH_ON_DELIVERY'
    CUSTOM = 'CUSTOM'
    GIFT_CARD = 'GIFT_CARD'
    MANUAL = 'MANUAL'
    MONEY_ORDER = 'MONEY_ORDER'
    SHOPIFY_INSTALLMENTS = 'SHOPIFY_INSTALLMENTS'


class TransactionTypeDetails(EmbeddedDocument):
    message = StringField(help_text="The message of the transaction type.")
    name = StringField(help_text="The name of the transaction type.")


# class OrderTransaction(EmbeddedDocument):
#     createdAt = DateTimeField(required=True)
#     giftCardDetails = EmbeddedDocumentField(GiftCardDetails)
#     shopify_id = StringField(required=True,unique=True, help_text="Globally unique identifier.")
#     kind = StringField(choices=[(kind.value, kind.name) for kind in OrderTransactionKind], required=True)
#     paymentDetails = EmbeddedDocumentField(PaymentDetails)
#     processedAt = DateTimeField()
#     status = StringField()
#     transactionAmount = EmbeddedDocumentField(MoneyBag, required=True, help_text="The amount of the transaction.")
#     transactionParentId = StringField()
#     type = StringField(choices=[(type.value, type.name) for type in OrderTransactionType], required=True)
#     typeDetails = EmbeddedDocumentField(TransactionTypeDetails)




class OrderTransactionErrorCode(Enum):
    AMAZON_PAYMENTS_INVALID_PAYMENT_METHOD = 'AMAZON_PAYMENTS_INVALID_PAYMENT_METHOD'
    AMAZON_PAYMENTS_MAX_AMOUNT_CHARGED = 'AMAZON_PAYMENTS_MAX_AMOUNT_CHARGED'
    AMAZON_PAYMENTS_MAX_AMOUNT_REFUNDED = 'AMAZON_PAYMENTS_MAX_AMOUNT_REFUNDED'
    AMAZON_PAYMENTS_MAX_AUTHORIZATIONS_CAPTURED = 'AMAZON_PAYMENTS_MAX_AUTHORIZATIONS_CAPTURED'
    AMAZON_PAYMENTS_MAX_REFUNDS_PROCESSED = 'AMAZON_PAYMENTS_MAX_REFUNDS_PROCESSED'
    AMAZON_PAYMENTS_ORDER_REFERENCE_CANCELED = 'AMAZON_PAYMENTS_ORDER_REFERENCE_CANCELED'
    AMAZON_PAYMENTS_STALE = 'AMAZON_PAYMENTS_STALE'
    CALL_ISSUER = 'CALL_ISSUER'
    CARD_DECLINED = 'CARD_DECLINED'
    CONFIG_ERROR = 'CONFIG_ERROR'
    EXPIRED_CARD = 'EXPIRED_CARD'
    GENERIC_ERROR = 'GENERIC_ERROR'
    INCORRECT_ADDRESS = 'INCORRECT_ADDRESS'
    INCORRECT_CVC = 'INCORRECT_CVC'
    INCORRECT_NUMBER = 'INCORRECT_NUMBER'
    INCORRECT_PIN = 'INCORRECT_PIN'
    INCORRECT_ZIP = 'INCORRECT_ZIP'
    INVALID_AMOUNT = 'INVALID_AMOUNT'
    INVALID_COUNTRY = 'INVALID_COUNTRY'
    INVALID_CVC = 'INVALID_CVC'
    INVALID_EXPIRY_DATE = 'INVALID_EXPIRY_DATE'
    INVALID_NUMBER = 'INVALID_NUMBER'
    PAYMENT_METHOD_UNAVAILABLE = 'PAYMENT_METHOD_UNAVAILABLE'
    PICK_UP_CARD = 'PICK_UP_CARD'
    PROCESSING_ERROR = 'PROCESSING_ERROR'
    TEST_MODE_LIVE_CARD = 'TEST_MODE_LIVE_CARD'
    UNSUPPORTED_FEATURE = 'UNSUPPORTED_FEATURE'



class TransactionFee(Document):
    shopify_id = StringField(required=True, unique=True, help_text="Globally unique identifier.")
    amount = EmbeddedDocumentField(MoneyV2, required=True, help_text="Amount of the fee.")
    flatFee = EmbeddedDocumentField(MoneyV2, required=True, help_text="Flat rate charge for a transaction.")
    flatFeeName = StringField(help_text="Name of the credit card flat fee.")
    rate = DecimalField(required=True, help_text="Percentage charge.")
    rateName = StringField(help_text="Name of the credit card rate.")
    taxAmount = EmbeddedDocumentField(MoneyV2, required=True, help_text="Tax amount charged on the fee.")
    type = StringField(required=True, help_text="Name of the type of fee.")


class ShopifyPaymentsExtendedAuthorization(EmbeddedDocument):

    extendedAuthorizationExpiresAt = DateTimeField(help_text="The time after which the extended authorization expires. After the expiry, the merchant is unable to capture the payment.")
    standardAuthorizationExpiresAt = DateTimeField( help_text="The time after which capture will incur an additional fee.")

class OrderTransactionStatus(Enum):

    AWAITING_RESPONSE = 'AWAITING_RESPONSE'
    ERROR = 'ERROR'
    FAILURE = 'FAILURE'
    PENDING = 'PENDING'
    SUCCESS = 'SUCCESS'
    UNKNOWN = 'UNKNOWN'


class StaffMemberPrivateData(EmbeddedDocument):
    accountSettingsUrl = URLField()
    createdAt = DateTimeField(required=True)


class StaffMember(Document):
    email = EmailField(required=True, unique=True)
    firstName = StringField(required=True)
    lastName = StringField(required=True)
    shopify_id = StringField(required=True, unique=True, help_text="Globally unique identifier.")

    active = BooleanField(required=True)
    avatar = EmbeddedDocumentField(Image)
    initials = ListField(StringField())
    email = EmailField(required=True)
    exists = BooleanField(required=True)
    firstName = StringField()
    shopify_id = StringField(required=True, unique=True)
    initials = ListField(StringField())
    isShopOwner = BooleanField(required=True)
    lastName = StringField()
    locale = StringField(required=True)
    name = StringField(required=True)
    phone = StringField()
    privateData = EmbeddedDocumentField('StaffMemberPrivateData')


class ShopifyPaymentsRefundSet(EmbeddedDocument):
    acquirerReferenceNumber = StringField()

class ShopifyPaymentsTransactionSet(EmbeddedDocument):
    extendedAuthorizationSet = EmbeddedDocumentField(ShopifyPaymentsExtendedAuthorization)
    refundSet = EmbeddedDocumentField(ShopifyPaymentsRefundSet)


class OrderTransaction(Document):
    shopify_id = StringField(required=True, unique=True, help_text="Globally unique identifier.")
    accountNumber = StringField()
    amountSet = EmbeddedDocumentField(MoneyBag, required=True)
    authorizationCode = StringField()
    authorizationExpiresAt = DateTimeField()
    createdAt = DateTimeField(required=True)
    errorCode = EnumField(OrderTransactionErrorCode)
    fees = ListField(LazyReferenceField(TransactionFee), required=True)
    formattedGateway = StringField()
    gateway = StringField()
    shopify_id = StringField(required=True, unique=True, help_text="Globally unique identifier.")
    kind = EnumField(OrderTransactionKind, required=True)
    manuallyCapturable = BooleanField(required=True)
    maximumRefundableV2 = EmbeddedDocumentField(MoneyV2)
    multiCapturable = BooleanField(required=True)
    order = LazyReferenceField('Order')
    parentTransaction = LazyReferenceField('OrderTransaction')
    # paymentDetails = EmbeddedDocumentField('PaymentDetails')
    paymentIcon = EmbeddedDocumentField(Image)
    paymentId = StringField()
    processedAt = DateTimeField()
    receiptJson = StringField()
    settlementCurrency = EnumField(CurrencyCode)
    settlementCurrencyRate = DecimalField()
    shopifyPaymentsSet = EmbeddedDocumentField(ShopifyPaymentsTransactionSet)
    status = EnumField(OrderTransactionStatus, required=True)
    test = BooleanField(required=True)
    totalUnsettledSet = EmbeddedDocumentField(MoneyBag)
    user = LazyReferenceField('StaffMember')



class OrderCancelReason(Enum):
    CUSTOMER = 'CUSTOMER'
    DECLINED = 'DECLINED'
    FRAUD = 'FRAUD'
    INVENTORY = 'INVENTORY'
    OTHER = 'OTHER'
    STAFF = 'STAFF'


class OrderFinancialStatus(Enum):
    AUTHORIZED = 'AUTHORIZED'
    PAID = 'PAID'
    PARTIALLY_PAID = 'PARTIALLY_PAID'
    PARTIALLY_REFUNDED = 'PARTIALLY_REFUNDED'
    PENDING = 'PENDING'
    REFUNDED = 'REFUNDED'
    VOIDED = 'VOIDED'


class OrderPaymentStatus(Enum):
    AUTHORIZED = 'AUTHORIZED'
    EXPIRED = 'EXPIRED'
    PAID = 'PAID'
    PARTIALLY_PAID = 'PARTIALLY_PAID'
    PARTIALLY_REFUNDED = 'PARTIALLY_REFUNDED'
    PENDING = 'PENDING'
    REFUNDED = 'REFUNDED'
    VOIDED = 'VOIDED'


class PaymentTermsType(Enum):
    FIXED = 'FIXED'
    FULFILLMENT = 'FULFILLMENT'
    NET = 'NET'
    RECEIPT = 'RECEIPT'
    UNKNOWN = 'UNKNOWN'



class PaymentTerms(Document):
    shopify_id = StringField(unique=True, sparse=True, help_text="A globally-unique ID.")
    # draftOrder = LazyReferenceField('DraftOrder', help_text="The draft order associated with the payment terms.")
    dueInDays = IntField(help_text="The number of days before the payment is due.")
    order = LazyReferenceField('Order', help_text="The order associated with the payment terms.")
    overdue = BooleanField(required=True, help_text="Whether the payment terms have overdue payment schedules.")
    paymentTermsName = StringField(required=True, help_text="The name of the payment terms template that was used to create the payment terms.")
    paymentTermsType = StringField(choices=[(type.value, type.name) for type in PaymentTermsType], required=True, help_text="The type of payment terms.")
    translatedName = StringField(help_text="The payment terms name, translated into the shop admin's preferred language..")

class OrderPaymentInformation(Document):
    paymentCollectionUrl = URLField(help_text="The URL for collecting a payment on the order.")
    paymentStatus = StringField(choices=[(status.value, status.name) for status in OrderPaymentStatus], help_text="The financial status of the order.")
    paymentTerms = LazyReferenceField('PaymentTerms')
    totalOutstandingAmount = EmbeddedDocumentField(MoneyV2, required=True, help_text="The total amount that's yet to be transacted for the order.")
    totalPaidAmount = EmbeddedDocumentField(MoneyV2, required=True, help_text="The total amount that has been paid for the order before any refund.")


class Refund(EmbeddedDocument):
    createdAt = DateTimeField(required=True)
    shopify_id = StringField(required=True, unique=True, help_text="Globally unique identifier.")
    returnName = StringField()
    totalRefunded = EmbeddedDocumentField(MoneyV2, required=True)





class AdditionalFee(Document):
    shopify_id = StringField(required=True, unique=True, sparse=True, help_text="A globally-unique ID.")
    name = StringField(required=True, help_text="The name of the additional fee.")
    price = EmbeddedDocumentField(MoneyBag, required=True, help_text="The price of the additional fee.")
    taxLines = ListField(EmbeddedDocumentField(TaxLine), required=True, help_text="A list of taxes charged on the additional fee.")


class OrderApp(Document):
    icon = EmbeddedDocumentField(Image, required=True, help_text="The application icon.")
    shopify_id = StringField(required=True, unique=True, help_text="The application ID.")
    name = StringField(required=True, help_text="The name of the application.")

class MailingAddress(Document):
    address1 = StringField(help_text="The first line of the address. Typically the street address or PO Box number.")
    address2 = StringField(help_text="The second line of the address. Typically the number of the apartment, suite, or unit.")
    city = StringField(help_text="The name of the city, district, village, or town.")
    company = StringField(help_text="The name of the customer's company or organization.")
    coordinatesValidated = BooleanField(required=True, help_text="Whether the address coordinates are valid.")
    country = StringField(help_text="The name of the country.")
    countryCodeV2 = StringField(help_text="The two-letter code for the country of the address.")
    firstName = StringField(help_text="The first name of the customer.")
    # formatted = ListField(StringField(), required=True, help_text="A formatted version of the address, customized by the provided arguments.")
    formattedArea = StringField(help_text="A comma-separated list of the values for city, province, and country.")
    shopify_id = StringField(required=True, unique=True, help_text="A globally-unique ID.")
    lastName = StringField(help_text="The last name of the customer.")
    latitude = FloatField(help_text="The latitude coordinate of the customer address.")
    longitude = FloatField(help_text="The longitude coordinate of the customer address.")
    name = StringField(help_text="The full name of the customer, based on firstName and lastName.")
    phone = StringField(help_text="A unique phone number for the customer. Formatted using E.164 standard. For example, +16135551111.")
    province = StringField(help_text="The region of the address, such as the province, state, or district.")
    provinceCode = StringField(help_text="The two-letter code for the region.")
    timeZone = StringField(help_text="The time zone of the address.")
    zip = StringField(help_text="The zip or postal code of the address.")


class OrderCancellation(EmbeddedDocument):
    staffNote = StringField(help_text="Staff provided note for the order cancellation.")


class ChannelDefinition(EmbeddedDocument):
    channelName = StringField(required=True, help_text="Name of the channel that this sub channel belongs to.")
    handle = StringField(required=True, help_text="Unique string used as a public identifier for the channel definition.")
    shopify_id = StringField(required=True, unique_id = True, help_text="The unique ID for the channel definition.")
    isMarketplace = BooleanField(required=True, help_text="Whether this channel definition represents a marketplace.")
    subChannelName = StringField(required=True, help_text="Name of the sub channel (e.g. Online Store, Instagram Shopping, TikTok Live).")
    svgIcon = StringField(help_text="Icon displayed when showing the channel in admin.")


# class ChannelInformation(EmbeddedDocument):
#     app = EmbeddedDocumentField(App, required=True, help_text="The app associated with the channel.")
#     channelDefinition = EmbeddedDocumentField(ChannelDefinition, help_text="The channel definition associated with the channel.")
#     channelId = StringField(required=True, help_text="The unique ID for the channel.")
#     id = StringField(required=True, help_text="A globally-unique ID.")

class Attribute(EmbeddedDocument):
    key = StringField(required=True, help_text="Key or name of the attribute.")
    value = StringField(help_text="Value of the attribute.")

class OrderDisplayFinancialStatus(Enum):
    AUTHORIZED = 'AUTHORIZED'
    EXPIRED = 'EXPIRED'
    PAID = 'PAID'
    PARTIALLY_PAID = 'PARTIALLY_PAID'
    PARTIALLY_REFUNDED = 'PARTIALLY_REFUNDED'
    PENDING = 'PENDING'
    REFUNDED = 'REFUNDED'
    VOIDED = 'VOIDED'

class OrderDisplayFulfillmentStatus(Enum):
    FULFILLED = 'FULFILLED'
    IN_PROGRESS = 'IN_PROGRESS'
    ON_HOLD = 'ON_HOLD'
    OPEN = 'OPEN'
    PARTIALLY_FULFILLED = 'PARTIALLY_FULFILLED'
    PENDING_FULFILLMENT = 'PENDING_FULFILLMENT'
    RESTOCKED = 'RESTOCKED'
    SCHEDULED = 'SCHEDULED'
    UNFULFILLED = 'UNFULFILLED'

class DisputeType(Enum):
    CHARGEBACK = 'CHARGEBACK'
    INQUIRY = 'INQUIRY'

class DisputeStatus(Enum):
    ACCEPTED = 'ACCEPTED'
    LOST = 'LOST'
    NEEDS_RESPONSE = 'NEEDS_RESPONSE'
    UNDER_REVIEW = 'UNDER_REVIEW'
    WON = 'WON'
    CHARGE_REFUNDED = 'CHARGE_REFUNDED'

class OrderDisputeSummary(Document):
    shopify_id = StringField( unique=True, sparse=True, help_text="A globally-unique ID.")
    initiatedAs = StringField(choices=[(type.value, type.name) for type in DisputeType], required=True, help_text="The type that the dispute was initiated as.")
    status = StringField(choices=[(status.value, status.name) for status in DisputeStatus], required=True, help_text="The current status of the dispute.")


class CountryCode(Enum):
    AC = "Ascension Island"
    AD = "Andorra"
    AE = "United Arab Emirates"
    AF = "Afghanistan"
    AG = "Antigua & Barbuda"
    AI = "Anguilla"
    AL = "Albania"
    AM = "Armenia"
    AN = "Netherlands Antilles"
    AO = "Angola"
    AR = "Argentina"
    AT = "Austria"
    AU = "Australia"
    AW = "Aruba"
    AX = "Åland Islands"
    AZ = "Azerbaijan"
    BA = "Bosnia & Herzegovina"
    BB = "Barbados"
    BD = "Bangladesh"
    BE = "Belgium"
    BF = "Burkina Faso"
    BG = "Bulgaria"
    BH = "Bahrain"
    BI = "Burundi"
    BJ = "Benin"
    BL = "St. Barthélemy"
    BM = "Bermuda"
    BN = "Brunei"
    BO = "Bolivia"
    BQ = "Caribbean Netherlands"
    BR = "Brazil"
    BS = "Bahamas"
    BT = "Bhutan"
    BV = "Bouvet Island"
    BW = "Botswana"
    BY = "Belarus"
    BZ = "Belize"
    CA = "Canada"
    CC = "Cocos (Keeling) Islands"
    CD = "Congo - Kinshasa"
    CF = "Central African Republic"
    CG = "Congo - Brazzaville"
    CH = "Switzerland"
    CI = "Côte d’Ivoire"
    CK = "Cook Islands"
    CL = "Chile"
    CM = "Cameroon"
    CN = "China"
    CO = "Colombia"
    CR = "Costa Rica"
    CU = "Cuba"
    CV = "Cape Verde"
    CW = "Curaçao"
    CX = "Christmas Island"
    CY = "Cyprus"
    CZ = "Czechia"
    DE = "Germany"
    DJ = "Djibouti"
    DK = "Denmark"
    DM = "Dominica"
    DO = "Dominican Republic"
    DZ = "Algeria"
    EC = "Ecuador"
    EE = "Estonia"
    EG = "Egypt"
    EH = "Western Sahara"
    ER = "Eritrea"
    ES = "Spain"
    ET = "Ethiopia"
    FI = "Finland"
    FJ = "Fiji"
    FK = "Falkland Islands"
    FO = "Faroe Islands"
    FR = "France"
    GA = "Gabon"
    GB = "United Kingdom"
    GD = "Grenada"
    GE = "Georgia"
    GF = "French Guiana"
    GG = "Guernsey"
    GH = "Ghana"
    GI = "Gibraltar"
    GL = "Greenland"
    GM = "Gambia"
    GN = "Guinea"
    GP = "Guadeloupe"
    GQ = "Equatorial Guinea"
    GR = "Greece"
    GS = "South Georgia & South Sandwich Islands"
    GT = "Guatemala"
    GW = "Guinea-Bissau"
    GY = "Guyana"
    HK = "Hong Kong SAR"
    HM = "Heard & McDonald Islands"
    HN = "Honduras"
    HR = "Croatia"
    HT = "Haiti"
    HU = "Hungary"
    ID = "Indonesia"
    IE = "Ireland"
    IL = "Israel"
    IM = "Isle of Man"
    IN = "India"
    IO = "British Indian Ocean Territory"
    IQ = "Iraq"
    IR = "Iran"
    IS = "Iceland"
    IT = "Italy"
    JE = "Jersey"
    JM = "Jamaica"
    JO = "Jordan"
    JP = "Japan"
    KE = "Kenya"
    KG = "Kyrgyzstan"
    KH = "Cambodia"
    KI = "Kiribati"
    KM = "Comoros"
    KN = "St. Kitts & Nevis"
    KP = "North Korea"
    KR = "South Korea"
    KW = "Kuwait"
    KY = "Cayman Islands"
    KZ = "Kazakhstan"
    LA = "Laos"
    LB = "Lebanon"
    LC = "St. Lucia"
    LI = "Liechtenstein"
    LK = "Sri Lanka"
    LR = "Liberia"
    LS = "Lesotho"
    LT = "Lithuania"
    LU = "Luxembourg"
    LV = "Latvia"
    LY = "Libya"
    MA = "Morocco"
    MC = "Monaco"
    MD = "Moldova"
    ME = "Montenegro"
    MF = "St. Martin"
    MG = "Madagascar"
    MK = "North Macedonia"
    ML = "Mali"
    MM = "Myanmar (Burma)"
    MN = "Mongolia"
    MO = "Macao SAR"
    MQ = "Martinique"
    MR = "Mauritania"
    MS = "Montserrat"
    MT = "Malta"
    MU = "Mauritius"
    MV = "Maldives"
    MW = "Malawi"
    MX = "Mexico"
    MY = "Malaysia"
    MZ = "Mozambique"
    NA = "Namibia"
    NC = "New Caledonia"
    NE = "Niger"
    NF = "Norfolk Island"
    NG = "Nigeria"
    NI = "Nicaragua"
    NL = "Netherlands"
    NO = "Norway"
    NP = "Nepal"
    NR = "Nauru"
    NU = "Niue"
    NZ = "New Zealand"
    OM = "Oman"
    PA = "Panama"
    PE = "Peru"
    PF = "French Polynesia"
    PG = "Papua New Guinea"
    PH = "Philippines"
    PK = "Pakistan"
    PL = "Poland"
    PM = "St. Pierre & Miquelon"
    PN = "Pitcairn Islands"
    PS = "Palestinian Territories"
    PT = "Portugal"
    PY = "Paraguay"
    QA = "Qatar"
    RE = "Réunion"
    RO = "Romania"
    RS = "Serbia"
    RU = "Russia"
    RW = "Rwanda"
    SA = "Saudi Arabia"
    SB = "Solomon Islands"
    SC = "Seychelles"
    SD = "Sudan"
    SE = "Sweden"
    SG = "Singapore"
    SH = "St. Helena"
    SI = "Slovenia"
    SJ = "Svalbard & Jan Mayen"
    SK = "Slovakia"
    SL = "Sierra Leone"
    SM = "San Marino"
    SN = "Senegal"
    SO = "Somalia"
    SR = "Suriname"
    SS = "South Sudan"
    ST = "São Tomé & Príncipe"
    SV = "El Salvador"
    SX = "Sint Maarten"
    SY = "Syria"
    SZ = "Eswatini"
    TA = "Tristan da Cunha"
    TC = "Turks & Caicos Islands"
    TD = "Chad"
    TF = "French Southern Territories"
    TG = "Togo"
    TH = "Thailand"
    TJ = "Tajikistan"
    TK = "Tokelau"
    TL = "Timor-Leste"
    TM = "Turkmenistan"
    TN = "Tunisia"
    TO = "Tonga"
    TR = "Türkiye"
    TT = "Trinidad & Tobago"
    TV = "Tuvalu"
    TW = "Taiwan"
    TZ = "Tanzania"
    UA = "Ukraine"
    UG = "Uganda"
    UM = "U.S. Outlying Islands"
    US = "United States"
    UY = "Uruguay"
    UZ = "Uzbekistan"
    VA = "Vatican City"
    VC = "St. Vincent & Grenadines"
    VE = "Venezuela"
    VG = "British Virgin Islands"
    VN = "Vietnam"
    VU = "Vanuatu"
    WF = "Wallis & Futuna"
    WS = "Samoa"
    XK = "Kosovo"
    YE = "Yemen"
    YT = "Mayotte"
    ZA = "South Africa"
    ZM = "Zambia"
    ZW = "Zimbabwe"
    ZZ = "Unknown Region"



class CustomerCreditCardBillingAddress(EmbeddedDocument):
    address1 = StringField(help_text="The first line of the address. Typically the street address or PO Box number.")
    city = StringField(help_text="The name of the city, district, village, or town.")
    country = StringField(help_text="The name of the country.")
    countryCode = StringField(choices=[(code.value, code.name) for code in CountryCode], help_text="The two-letter code for the country of the address. For example, US.")
    firstName = StringField(help_text="The first name in the billing address.")
    lastName = StringField(help_text="The last name in the billing address.")
    province = StringField(help_text="The region of the address, such as the province, state, or district.")
    provinceCode = StringField(help_text="The two-letter code for the region. For example, ON.")
    zip = StringField(help_text="The zip or postal code of the address.")


class VaultCreditCard(EmbeddedDocument):
    billingAddress = EmbeddedDocumentField(CustomerCreditCardBillingAddress)
    brand = StringField(required=True, help_text="The brand for the card.")
    expired = BooleanField(required=True, help_text="Whether the card has been expired.")
    expiryMonth = IntField(required=True, help_text="The expiry month of the card.")
    expiryYear = IntField(required=True, help_text="The expiry year of the card.")
    lastDigits = StringField(required=True, help_text="The last four digits for the card.")
    name = StringField(required=True, help_text="The name of the card holder.")


class VaultPaypalBillingAgreement(EmbeddedDocument):
    inactive = BooleanField(required=True, help_text="Whether the paypal billing agreement is inactive.")
    name = StringField(required=True, help_text="The paypal account name.")
    paypalAccountEmail = StringField(required=True, help_text="The paypal account email address.")


class PaymentInstrument(Document):
    VaultCreditCard = EmbeddedDocumentField(VaultCreditCard)
    VaultPaypalBillingAgreement = EmbeddedDocumentField(VaultPaypalBillingAgreement)

class PaymentMandate(Document):
    shopify_id = StringField(required=True, unique_id=True, help_text="The unique ID of a payment mandate.")
    paymentInstrument = LazyReferenceField(PaymentInstrument, required=True, help_text="The outputs details of the payment instrument.")

class OrderPaymentCollectionDetails(EmbeddedDocument):
    additionalPaymentCollectionUrl = URLField(help_text="The URL to use for collecting an additional payment on the order.")
    vaultedPaymentMethods = ListField(LazyReferenceField(PaymentMandate), help_text="The list of vaulted payment methods for the order with their permissions.")

class OrderReturnStatus(Enum):
    INSPECTION_COMPLETE = "INSPECTION_COMPLETE"
    IN_PROGRESS = "IN_PROGRESS"
    NO_RETURN = "NO_RETURN"
    RETURNED = "RETURNED"
    RETURN_FAILED = "RETURN_FAILED"
    RETURN_REQUESTED = "RETURN_REQUESTED"



# customer
class CustomerMarketingOptInLevel(Enum):
    CONFIRMED_OPT_IN = "CONFIRMED_OPT_IN"
    SINGLE_OPT_IN = "SINGLE_OPT_IN"
    UNKNOWN = "UNKNOWN"



class CustomerEmailMarketingState(Enum):
    INVALID = "INVALID"
    NOT_SUBSCRIBED = "NOT_SUBSCRIBED"
    PENDING = "PENDING"
    REDACTED = "REDACTED"
    SUBSCRIBED = "SUBSCRIBED"
    UNSUBSCRIBED = "UNSUBSCRIBED"


class CustomerEmailMarketingConsentState(EmbeddedDocument):
    consentUpdatedAt = DateTimeField(help_text="The date and time at which the customer consented to receive marketing material by email.")
    marketingOptInLevel = EnumField(CustomerMarketingOptInLevel, help_text="The marketing subscription opt-in level that the customer gave when they consented to receive marketing material by email.")
    marketingState = EnumField(CustomerEmailMarketingState, required=True, help_text="The current email marketing state for the customer.")


class CountPrecision(Enum):
    AT_LEAST = "AT_LEAST"
    EXACT = "EXACT"

class Count(EmbeddedDocument):
    count = IntField(required=True, help_text="Count of elements.")
    precision = EnumField(CountPrecision, required=True, help_text="Precision of count, how exact is the value.")


class CurrencySetting(EmbeddedDocument):
    currencyCode = EnumField(CurrencyCode, required=True, help_text="The currency's ISO code.")
    currencyName = StringField(required=True, help_text="The full name of the currency.")
    enabled = BooleanField(required=True, help_text="Whether the currency is enabled or not. An enabled currency setting is visible to buyers and allows orders to be generated with that currency as presentment.")
    rateUpdatedAt = DateTimeField(help_text="The date and time when the active exchange rate for the currency was last modified. It can be the automatic rate's creation date, or the manual rate's last updated at date if active.")


class MarketCurrencySettings(EmbeddedDocument):
    baseCurrency = EmbeddedDocumentField(CurrencySetting, required=True, help_text="The currency which this market's prices are defined in, and the currency which its customers must use if local currencies are disabled.")
    localCurrencies = BooleanField(required=True, help_text="Whether local currencies are enabled for the market.")



class Market(Document):
    catalogsCount = EmbeddedDocumentField(Count, help_text="The number of catalogs that belong to the market.")
    currencySettings = EmbeddedDocumentField(MarketCurrencySettings, required=True, help_text="The market’s currency settings.")
    enabled = BooleanField(required=True, help_text="Whether the market is enabled to receive visitors and sales.")
    handle = StringField(required=True, help_text="A short, human-readable unique identifier for the market.")
    shopify_id = StringField(required=True, help_text="A globally-unique ID.")
    # metafield = EmbeddedDocumentField(Metafield, help_text="Returns a metafield by namespace and key that belongs to the resource.")
    name = StringField(required=True, help_text="The name of the market. Not shown to customers.")
    primary = BooleanField(required=True, help_text="Whether the market is the shop’s primary market.")
    # webPresence = EmbeddedDocumentField(MarketWebPresence, help_text="The market’s web presence, which defines its SEO strategy.")



class CustomerMergeErrorFieldType(Enum):
    COMPANY_CONTACT = "COMPANY_CONTACT"
    CUSTOMER_PAYMENT_METHODS = "CUSTOMER_PAYMENT_METHODS"
    DELETED_AT = "DELETED_AT"
    GIFT_CARDS = "GIFT_CARDS"
    MERGE_IN_PROGRESS = "MERGE_IN_PROGRESS"
    MULTIPASS_IDENTIFIER = "MULTIPASS_IDENTIFIER"
    PENDING_DATA_REQUEST = "PENDING_DATA_REQUEST"
    REDACTED_AT = "REDACTED_AT"
    SUBSCRIPTIONS = "SUBSCRIPTIONS"

class CustomerMergeError(EmbeddedDocument):
    errorFields = ListField(EnumField(CustomerMergeErrorFieldType), required=True, help_text="The list of fields preventing the customer from being merged.")
    message = StringField(required=True, help_text="The customer merge error message.")


class CustomerMergeRequestStatus(Enum):
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    IN_PROGRESS = "IN_PROGRESS"
    REQUESTED = "REQUESTED"


class CustomerMergeRequest(EmbeddedDocument):
    customerMergeErrors = ListField(EmbeddedDocumentField(CustomerMergeError), required=True, help_text="The merge errors that occurred during the customer merge request.")
    jobId = StringField(required=True, help_text="The UUID of the merge job.")
    resultingCustomerId = StringField(required=True, help_text="The ID of the customer resulting from the merge.")
    status = EnumField(CustomerMergeRequestStatus, required=True, help_text="The status of the customer merge request.")

class CustomerMergeable(Document):
    isMergeable = BooleanField(required=True, help_text="Whether the customer can be merged with another customer.")
    errorFields = ListField(EnumField(CustomerMergeErrorFieldType), required=True, help_text="The list of fields preventing the customer from being merged.")
    mergeInProgress = EmbeddedDocumentField(CustomerMergeRequest, help_text="The merge request if one is currently in progress.")
    reason = StringField(help_text="The reason why the customer can't be merged with another customer.")




class CustomerProductSubscriberStatus(Enum):
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"
    NEVER_SUBSCRIBED = "NEVER_SUBSCRIBED"
    PAUSED = "PAUSED"



class CustomerSmsMarketingState(Enum):
    NOT_SUBSCRIBED = "NOT_SUBSCRIBED"
    PENDING = "PENDING"
    REDACTED = "REDACTED"
    SUBSCRIBED = "SUBSCRIBED"
    UNSUBSCRIBED = "UNSUBSCRIBED"



class CustomerMarketingOptInLevel(Enum):
    CONFIRMED_OPT_IN = "CONFIRMED_OPT_IN"
    SINGLE_OPT_IN = "SINGLE_OPT_IN"
    UNKNOWN = "UNKNOWN"

class CustomerConsentCollectedFrom(Enum):
    OTHER = "OTHER"
    SHOPIFY = "SHOPIFY"


class CustomerSmsMarketingConsentState(EmbeddedDocument):
    consentUpdatedAt = DateTimeField(help_text="The date and time when the customer consented to receive marketing material by SMS. If no date is provided, then the date and time when the consent information was sent is used.")
    marketingOptInLevel = EnumField(CustomerMarketingOptInLevel, help_text="The marketing subscription opt-in level that was set when the customer consented to receive marketing information.")
    marketingState = EnumField(CustomerSmsMarketingState, required=True, help_text="The current SMS marketing state for the customer.")
    consentCollectedFrom = EnumField(CustomerConsentCollectedFrom, help_text="The source from which the SMS marketing information for the customer was collected.")


class CustomerState(Enum):
    DECLINED = "DECLINED"
    DISABLED = "DISABLED"
    ENABLED = "ENABLED"
    INVITED = "INVITED"

class CustomerPredictedSpendTier(Enum):
    HIGH = "HIGH"
    LOW = "LOW"
    MEDIUM = "MEDIUM"

class CustomerStatistics(EmbeddedDocument):
    predictedSpendTier = EnumField(CustomerPredictedSpendTier, help_text="The predicted spend tier of a customer with a shop.")
    # Add other fields here



class TaxExemption(Enum):
    CA_BC_COMMERCIAL_FISHERY_EXEMPTION = 'CA_BC_COMMERCIAL_FISHERY_EXEMPTION'
    CA_BC_CONTRACTOR_EXEMPTION = 'CA_BC_CONTRACTOR_EXEMPTION'
    CA_BC_PRODUCTION_AND_MACHINERY_EXEMPTION = 'CA_BC_PRODUCTION_AND_MACHINERY_EXEMPTION'
    CA_BC_RESELLER_EXEMPTION = 'CA_BC_RESELLER_EXEMPTION'
    CA_BC_SUB_CONTRACTOR_EXEMPTION = 'CA_BC_SUB_CONTRACTOR_EXEMPTION'
    CA_DIPLOMAT_EXEMPTION = 'CA_DIPLOMAT_EXEMPTION'
    CA_MB_COMMERCIAL_FISHERY_EXEMPTION = 'CA_MB_COMMERCIAL_FISHERY_EXEMPTION'
    CA_MB_FARMER_EXEMPTION = 'CA_MB_FARMER_EXEMPTION'
    CA_MB_RESELLER_EXEMPTION = 'CA_MB_RESELLER_EXEMPTION'
    CA_NS_COMMERCIAL_FISHERY_EXEMPTION = 'CA_NS_COMMERCIAL_FISHERY_EXEMPTION'
    CA_NS_FARMER_EXEMPTION = 'CA_NS_FARMER_EXEMPTION'
    CA_ON_PURCHASE_EXEMPTION = 'CA_ON_PURCHASE_EXEMPTION'
    CA_PE_COMMERCIAL_FISHERY_EXEMPTION = 'CA_PE_COMMERCIAL_FISHERY_EXEMPTION'
    CA_SK_COMMERCIAL_FISHERY_EXEMPTION = 'CA_SK_COMMERCIAL_FISHERY_EXEMPTION'
    CA_SK_CONTRACTOR_EXEMPTION = 'CA_SK_CONTRACTOR_EXEMPTION'
    CA_SK_FARMER_EXEMPTION = 'CA_SK_FARMER_EXEMPTION'
    CA_SK_PRODUCTION_AND_MACHINERY_EXEMPTION = 'CA_SK_PRODUCTION_AND_MACHINERY_EXEMPTION'
    CA_SK_RESELLER_EXEMPTION = 'CA_SK_RESELLER_EXEMPTION'
    CA_SK_SUB_CONTRACTOR_EXEMPTION = 'CA_SK_SUB_CONTRACTOR_EXEMPTION'
    CA_STATUS_CARD_EXEMPTION = 'CA_STATUS_CARD_EXEMPTION'
    EU_REVERSE_CHARGE_EXEMPTION_RULE = 'EU_REVERSE_CHARGE_EXEMPTION_RULE'
    US_AK_RESELLER_EXEMPTION = 'US_AK_RESELLER_EXEMPTION'
    US_AL_RESELLER_EXEMPTION = 'US_AL_RESELLER_EXEMPTION'
    US_AR_RESELLER_EXEMPTION = 'US_AR_RESELLER_EXEMPTION'
    US_AZ_RESELLER_EXEMPTION = 'US_AZ_RESELLER_EXEMPTION'
    US_CA_RESELLER_EXEMPTION = 'US_CA_RESELLER_EXEMPTION'
    US_CO_RESELLER_EXEMPTION = 'US_CO_RESELLER_EXEMPTION'
    US_CT_RESELLER_EXEMPTION = 'US_CT_RESELLER_EXEMPTION'
    US_DC_RESELLER_EXEMPTION = 'US_DC_RESELLER_EXEMPTION'
    US_DE_RESELLER_EXEMPTION = 'US_DE_RESELLER_EXEMPTION'
    US_FL_RESELLER_EXEMPTION = 'US_FL_RESELLER_EXEMPTION'
    US_GA_RESELLER_EXEMPTION = 'US_GA_RESELLER_EXEMPTION'
    US_HI_RESELLER_EXEMPTION = 'US_HI_RESELLER_EXEMPTION'
    US_IA_RESELLER_EXEMPTION = 'US_IA_RESELLER_EXEMPTION'
    US_ID_RESELLER_EXEMPTION = 'US_ID_RESELLER_EXEMPTION'
    US_IL_RESELLER_EXEMPTION = 'US_IL_RESELLER_EXEMPTION'
    US_IN_RESELLER_EXEMPTION = 'US_IN_RESELLER_EXEMPTION'
    US_KS_RESELLER_EXEMPTION = 'US_KS_RESELLER_EXEMPTION'
    US_KY_RESELLER_EXEMPTION = 'US_KY_RESELLER_EXEMPTION'
    US_LA_RESELLER_EXEMPTION = 'US_LA_RESELLER_EXEMPTION'
    US_MA_RESELLER_EXEMPTION = 'US_MA_RESELLER_EXEMPTION'
    US_MD_RESELLER_EXEMPTION = 'US_MD_RESELLER_EXEMPTION'
    US_ME_RESELLER_EXEMPTION = 'US_ME_RESELLER_EXEMPTION'
    US_MI_RESELLER_EXEMPTION = 'US_MI_RESELLER_EXEMPTION'
    US_MN_RESELLER_EXEMPTION = 'US_MN_RESELLER_EXEMPTION'
    US_MO_RESELLER_EXEMPTION = 'US_MO_RESELLER_EXEMPTION'
    US_MS_RESELLER_EXEMPTION = 'US_MS_RESELLER_EXEMPTION'
    US_MT_RESELLER_EXEMPTION = 'US_MT_RESELLER_EXEMPTION'
    US_NC_RESELLER_EXEMPTION = 'US_NC_RESELLER_EXEMPTION'
    US_ND_RESELLER_EXEMPTION = 'US_ND_RESELLER_EXEMPTION'
    US_NE_RESELLER_EXEMPTION = 'US_NE_RESELLER_EXEMPTION'
    US_NH_RESELLER_EXEMPTION = 'US_NH_RESELLER_EXEMPTION'
    US_NJ_RESELLER_EXEMPTION = 'US_NJ_RESELLER_EXEMPTION'
    US_NM_RESELLER_EXEMPTION = 'US_NM_RESELLER_EXEMPTION'
    US_NV_RESELLER_EXEMPTION = 'US_NV_RESELLER_EXEMPTION'
    US_NY_RESELLER_EXEMPTION = 'US_NY_RESELLER_EXEMPTION'
    US_OH_RESELLER_EXEMPTION = 'US_OH_RESELLER_EXEMPTION'
    US_OK_RESELLER_EXEMPTION = 'US_OK_RESELLER_EXEMPTION'
    US_OR_RESELLER_EXEMPTION = 'US_OR_RESELLER_EXEMPTION'
    US_PA_RESELLER_EXEMPTION = 'US_PA_RESELLER_EXEMPTION'
    US_RI_RESELLER_EXEMPTION = 'US_RI_RESELLER_EXEMPTION'
    US_SC_RESELLER_EXEMPTION = 'US_SC_RESELLER_EXEMPTION'
    US_SD_RESELLER_EXEMPTION = 'US_SD_RESELLER_EXEMPTION'
    US_TN_RESELLER_EXEMPTION = 'US_TN_RESELLER_EXEMPTION'
    US_TX_RESELLER_EXEMPTION = 'US_TX_RESELLER_EXEMPTION'
    US_UT_RESELLER_EXEMPTION = 'US_UT_RESELLER_EXEMPTION'
    US_VA_RESELLER_EXEMPTION = 'US_VA_RESELLER_EXEMPTION'
    US_VT_RESELLER_EXEMPTION = 'US_VT_RESELLER_EXEMPTION'
    US_WA_RESELLER_EXEMPTION = 'US_WA_RESELLER_EXEMPTION'
    US_WI_RESELLER_EXEMPTION = 'US_WI_RESELLER_EXEMPTION'
    US_WV_RESELLER_EXEMPTION = 'US_WV_RESELLER_EXEMPTION'
    US_WY_RESELLER_EXEMPTION = 'US_WY_RESELLER_EXEMPTION'
