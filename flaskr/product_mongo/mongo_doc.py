# fmt: off
from .basic_doc import *
from mongoengine import CASCADE, PULL, LazyReferenceField,ReferenceField,StringField,BooleanField,ListField,Document,IntField,URLField,EmbeddedDocumentField, DateTimeField, EmbeddedDocument



class Channel(Document):



    shopify_id = StringField(required=True, unique=True, help_text="A globally-unique identifier for the channel.")
    name = StringField(required=True, help_text="The name of the channel.")
    supportsFuturePublishing = BooleanField(required=True, help_text="Whether the channel supports future publishing.")
    handle = StringField(required=True, help_text="The unique identifier for the channel. Deprecated, use id instead.")
    navigationItems = ListField(LazyReferenceField('NavigationItem'), help_text="Menu items for the channel, deprecated. Use AppInstallation.navigationItems instead.")
    overviewPath = URLField(help_text="Home page URL for the channel. Deprecated, use AppInstallation.launchUrl instead.")
    productsCount = IntField(help_text="The count of products published to the channel, limited to a maximum of 10000.")

    meta = {
        'indexes': [
            'name',    # Index on name for quick lookup
        ],
        'ordering': ['name']    # Order by name by default
    }

class Collection(Document):

    shopify_id = StringField(required=True,unique=True, help_text="A globally-unique ID.")
    availablePublicationsCount = IntField(required=True, help_text="The number of publications a resource is published to without feedback errors.")
    description = StringField(required=True, help_text="A single-line, text-only description of the collection, stripped of any HTML tags.")
    descriptionHtml = StringField(required=True, help_text="The description of the collection, including any HTML tags and formatting.")
    handle = StringField(required=True, help_text="A unique string that identifies the collection, automatically generated from the title.")
    # hasProduct = BooleanField(required=True, help_text="Whether the collection includes the specified product.")
    legacyResourceId = StringField(required=True, help_text="The ID of the corresponding resource in the REST Admin API.")
    productsCount = IntField(help_text="The number of products in the collection.")
    publicationCount = IntField(help_text="The number of publications a resource is published on.")
    publishedOnCurrentPublication = BooleanField(required=True, help_text="Whether the resource is published to the calling app's publication.")
    # publishedOnPublication = BooleanField(required=True, help_text="Whether the resource is published to a given publication.")
    # seo = EmbeddedDocumentField(SEO, help_text="SEO details if modified from the default.")
    sortOrder = StringField(required=True, help_text="The default sort order for products in the collection.")
    templateSuffix = StringField(help_text="The suffix of the Liquid template being used.")
    title = StringField(required=True, help_text="The name of the collection.")
    # translations = ListField(EmbeddedDocumentField(Translation), help_text="Translations associated with the resource.")
    updatedAt = DateTimeField(required=True, help_text="The date and time when the collection was last updated.")
    image = EmbeddedDocumentField(Image, help_text="The image associated with the collection.")
    # metafield = EmbeddedDocumentField(Metafield, help_text="A metafield associated with the collection.")

    meta = {
        'indexes': [
            'handle',  # Index on handle for quick lookup.
            'legacyResourceId'  # Index on legacy resource ID if it's frequently accessed.
        ]
    }


class Publication(EmbeddedDocument):

    # reference fields
    channel = LazyReferenceField('Channel', required=True)
    isPublished = BooleanField(required=True)
    publishDate = DateTimeField()


class InventoryItem(Document):
    '''
    This class represents an inventory item in the Shopify store. pls refer to the Shopify API documentation for more information.
    https://shopify.dev/docs/api/admin-graphql/2024-04/queries/inventoryItem
    '''
    shopify_id = StringField(required=True, unique = True, help_text="A globally-unique identifier.")
    countryCodeOfOrigin = StringField(help_text="The ISO 3166-1 alpha-2 country code of where the item originated from.")
    createdAt = DateTimeField(default=datetime.now, required=True, help_text="The date and time when the inventory item was created.")
    duplicateSkuCount = IntField(required=True, help_text="The number of inventory items that share the same SKU.")
    harmonizedSystemCode = StringField(help_text="The harmonized system code of the item.")
    inventoryHistoryUrl = URLField(help_text="URL to the inventory history of the item.")
    legacyResourceId = StringField(required=True, help_text="The ID of the corresponding resource in the REST Admin API.")
    locationsCount = IntField(help_text="The number of locations where this inventory item is stocked.")
    provinceCodeOfOrigin = StringField(help_text="The ISO 3166-2 alpha-2 province code of where the item originated from.")
    requiresShipping = BooleanField(required=True, help_text="Whether the inventory item requires shipping.")
    sku = StringField(help_text="Case-sensitive SKU of the inventory item.")
    tracked = BooleanField(required=True, help_text="Whether inventory levels are tracked for this item.")
    updatedAt = DateTimeField(required=True, help_text="The date and time when the inventory item was last updated.")
    inventoryLevels = ListField(LazyReferenceField('InventoryLevel'), help_text="List of inventory levels associated with this item.")
    variant = LazyReferenceField(document_type='ProductVariant', required=True)
    unitCost = EmbeddedDocumentField(MoneyV2)

    meta = {'indexes': ['sku', 'legacyResourceId'], 'ordering': ['-createdAt']}



class ProductVariant(Document):
    '''
    This class represents a product variant in the Shopify store. Please refer to the Shopify API documentation for more information.
    https://shopify.dev/docs/api/admin-graphql/2024-04/queries/productVariant
    '''

    # reference fields
    product = LazyReferenceField('Product', required=True, help_text="The product associated with the product variant.")
    inventoryItem = LazyReferenceField('InventoryItem', required=True,reverse_delete_rule=None, help_text="The inventory item associated with the product variant.")

    availableForSale = BooleanField(required=True, help_text="Indicates whether the product variant is available for sale.")
    barcode = StringField(help_text="The barcode associated with the product variant.")
    compareAtPrice = StringField(help_text="The compare at price of the product variant. Usually represented as a string.")
    createdAt = DateTimeField(required=True, help_text="The date and time when the product variant was created.")
    defaultCursor = StringField(required=True, help_text="The default cursor of the product variant.")
    displayName = StringField(required=True, help_text="The display name of the product variant.")
    shopify_id = StringField(required=True, unique=True, help_text="The unique identifier of the product variant.")
    image = EmbeddedDocumentField(Image, help_text="The image associated with the product variant.")
    inventoryPolicy = StringField(required=True, help_text="The inventory policy of the product variant.")
    inventoryQuantity = IntField(help_text="The inventory quantity of the product variant.")
    legacyResourceId = StringField(required=True, help_text="The legacy resource ID of the product variant.")
    position = IntField(required=True, help_text="The position of the product variant.")
    price = StringField(required=True, help_text="The price of the product variant.")
    requiresComponents = BooleanField(required=True, help_text="Indicates whether the product variant requires components.")
    sellableOnlineQuantity = IntField(required=True, help_text="The sellable online quantity of the product variant.")
    sellingPlanGroupCount = IntField(help_text="The selling plan group count of the product variant.")
    sku = StringField(help_text="The SKU (stock keeping unit) of the product variant.")
    taxCode = StringField(help_text="The tax code associated with the product variant.")
    taxable = BooleanField(required=True, help_text="Indicates whether the product variant is taxable.")
    title = StringField(required=True, help_text="The title of the product variant.")
    updatedAt = DateTimeField(required=True, help_text="The date and time when the product variant was last updated.")
    weight = FloatField(help_text="The weight of the product variant.")
    weightUnit = StringField(required=True, help_text="The weight unit of the product variant.")

    meta = {
        'indexes': [
            'barcode',    # 索引条形码以优化Mongodb中的查询
            'sku',
            'title',
            'shopify_id'
            # 'id',
        ]
    }

class Product(Document):
    '''
    This class represents a product in the Shopify store. pls refer to the Shopify API documentation for more information.
    https://shopify.dev/docs/api/admin-graphql/2024-04/queries/product
    '''
    collections = ListField(LazyReferenceField('Collection', reverse_delete_rule=PULL),  help_text="List of collections that the product belongs to.")
    variants = ListField(LazyReferenceField(ProductVariant, reverse_delete_rule=PULL), help_text="List of variants associated with the product.")

    publications = ListField(EmbeddedDocumentField('Publication', ), help_text="List of publications the product is published to.") # 逆向删除待解决

    shopify_id = StringField(required=True,unique=True, help_text="A globally-unique identifier for the product.")
    title = StringField(required=True, help_text="The title of the product.")
    description = StringField(help_text="A stripped description of the product, single line with HTML tags removed.")
    productType = StringField(help_text="The product type specified by the merchant.")
    vendor = StringField(help_text="The name of the product's vendor.")
    status = StringField(help_text="The product status. This controls visibility across all channels.")
    tags = ListField(StringField(), help_text="A comma separated list of tags associated with the product.")
    featuredImage = EmbeddedDocumentField(Image, help_text="The featured image for the product.")
    onlineStoreUrl = URLField(help_text="The online store URL for the product.")
    priceRangeV2 = EmbeddedDocumentField(PriceRangeV2, help_text="The price range of the product with prices formatted as decimals.")
    createdAt = DateTimeField(required=True, help_text="The date and time (ISO 8601 format) when the product was created.")
    updatedAt = DateTimeField(required=True, help_text="The date and time when the product was last modified.")

    metafields = ListField(ReferenceField(Metafield), default=[], help_text="A list of metafields associated with the product.")
    options = ListField(ReferenceField(ProductOption), default = [])

    # 自增字段
    descriptionVector = ListField(FloatField(), default=lambda: [0.0] * 1024)

    handle = StringField(help_text="A human-friendly unique string for the product.")
    amount = IntField(help_text='Record the number of item sold for this product.')
    revenue = FloatField(help_text='Record the total revenue = amount * lineitem_price')

    meta = {
        'indexes': [
            'vendor',    # Example of setting an index on vendor field
            'status',
            'title',
            'description',
        ]
    }






class Customer(Document):
    '''
    This class represents a customer in the Shopify store. pls refer to the Shopify API documentation for more information.
    https://shopify.dev/docs/api/admin-graphql/2024-04/queries/customer
    '''

    shopify_id = StringField(required=True, unique=True,help_text="A globally-unique identifier for the customer.")
    addresses = ListField(ReferenceField(MailingAddress), required=True, help_text="List of mailing addresses.")
    canDelete = BooleanField(required=True, help_text="Whether the merchant can delete the customer from their store.")
    createdAt = DateTimeField(required=True, help_text="The date and time when the customer was created.")
    amountSpent = EmbeddedDocumentField(MoneyV2, required=True, help_text="The total amount that the customer has spent on orders in their lifetime.")
    # companyContactProfiles
    defaultAddress = ReferenceField(MailingAddress, default = None,help_text="The default address associated with the customer.")
    displayName = StringField(required=True, help_text="The full name of the customer, based on the values for first_name and last_name. If the first_name and last_name are not available, then this falls back to the customer's email address, and if that is not available, the customer's phone number.")
    email = EmailField(help_text="The email address of the customer.")
    emailMarketingConsent = EmbeddedDocumentField(CustomerEmailMarketingConsentState, help_text="The current email marketing state for the customer. If the customer doesn't have an email address, then this property is null.")
    firstName = StringField(help_text="The customer's first name.")
    image = EmbeddedDocumentField(Image, help_text="The image associated with the customer.")
    lastName = StringField(default=None,help_text="The customer's last name.")
    lastOrder = ReferenceField('Order', default = None, help_text="The customer's last order.")
    legacyResourceId = StringField(required=True, help_text="The ID of the corresponding resource in the REST Admin API.")
    lifetimeDuration = StringField(required=True, help_text="The amount of time since the customer was first added to the store.")
    locale = StringField(required=True, help_text="The customer's locale.")
    # market
    mergeable = BooleanField(required=True, help_text="Whether the customer can be merged with another customer.")
    multipassIdentifier = StringField(default = None,help_text="A unique identifier for the customer that's used with Multipass login.")
    note = StringField(default= None,help_text="A note about the customer.")
    numberOfOrders = IntField(required=True, help_text="The number of orders that the customer has made at the store in their lifetime.")
    phone = StringField(default=None,help_text="The customer's phone number.")
    productSubscriberStatus = StringField(required=True, help_text="Possible subscriber states of a customer defined by their subscription contracts.")
    smsMarketingConsent = EmbeddedDocumentField(CustomerSmsMarketingConsentState, default= None, help_text="The current SMS marketing state for the customer. If the customer doesn't have a phone number, then this property is null.")
    state = StringField(required=True, help_text="The state of the customer's account with the shop.")
    statistics = EmbeddedDocumentField(CustomerStatistics, help_text="The statistics of the customer.")
    tags = ListField(StringField(), help_text="Tags associated with the customer.")
    taxExempt = BooleanField(required=True, help_text="Whether the customer is exempt from paying taxes on their order.")
    taxExemptions = ListField(EnumField(TaxExemption, required=True), required=True, help_text="The tax exemptions associated with the customer.")
    unsubscribeUrl = URLField(help_text="The URL to unsubscribe the customer from the mailing list.")
    updatedAt = DateTimeField(required=True, help_text="The date and time when the customer was last updated.")
    validEmailAddress = BooleanField(required=True, help_text="Whether the email address is formatted correctly.")
    verifiedEmail = BooleanField(required=True, help_text="Whether the customer has verified their email address. Defaults to true if the customer is created through the Shopify admin or API.")

    meta = {
        'indexes': ['email', 'phone'],
        'ordering': ['-creationDate']
    }


class Order(Document):
    '''
    This is a class representing an order in the Shopify store. pls refer to the Shopify API documentation for more information.
    https://shopify.dev/docs/api/admin-graphql/2024-04/queries/order
    '''
    customer = LazyReferenceField('Customer', help_text="The customer that placed the order.") # customer删除了，订单还会在，一般不会删除
    merchantOfRecordApp = ReferenceField('OrderApp', help_text="The application acting as the Merchant of Record for the order.") # 一般不会删除

    additionalFees = ListField(ReferenceField(AdditionalFee), required=False, help_text="A list of additional fees applied to the order.")

    # alerts = ListField(EmbeddedDocumentField(ResourceAlert), required=True, help_text="A list of messages that appear on the order page in the Shopify admin.")
    app = ReferenceField('OrderApp', help_text="The application that created the order.")
    billingAddress = ReferenceField(MailingAddress, help_text="The billing address of the customer.")
    billingAddressMatchesShippingAddress = BooleanField(required=True, help_text="Whether the billing address matches the shipping address.")
    canMarkAsPaid = BooleanField(required=True, help_text="Whether the order can be manually marked as paid.")
    canNotifyCustomer = BooleanField(required=True, help_text="Whether a customer email exists for the order.")
    cancelReason = EnumField(OrderCancelReason, help_text="The reason provided when the order was canceled. Returns null if the order wasn't canceled.")
    cancellation = EmbeddedDocumentField(OrderCancellation, help_text="Cancellation details for the order.")
    staffNote = StringField(help_text="Staff provided note for the order cancellation.")
    cancelledAt = DateTimeField(help_text="The date and time when the order was canceled. Returns null if the order wasn't canceled.")
    capturable = BooleanField(required=True, help_text="Whether payment for the order can be captured.")
    cartDiscountAmountSet = EmbeddedDocumentField(MoneyBag, help_text="The total order-level discount amount, before returns, in shop and presentment currencies.")
    # channelInformation = EmbeddedDocumentField(ChannelInformation, help_text="Details about the channel that created the order.")
    clientIp = StringField(help_text="The IP address of the API client that created the order.")
    closed = BooleanField(help_text="Whether the order is closed.")
    closedAt = DateTimeField(help_text="The date and time when the order was closed. Returns null if the order isn't closed.")
    confirmationNumber = StringField(help_text="A randomly generated alpha-numeric identifier for the order that may be shown to the customer instead of the sequential order name.")
    confirmed = BooleanField(required=True, help_text="Whether inventory has been reserved for the order.")
    createdAt = DateTimeField(required=True, help_text="Date and time when the order was created in Shopify.")
    currencyCode = EnumField(CurrencyCode, required=True, help_text="The shop currency when the order was placed.")
    currentCartDiscountAmountSet = EmbeddedDocumentField(MoneyBag, required=True, help_text="The current order-level discount amount after all order updates, in shop and presentment currencies.")
    currentSubtotalLineItemsQuantity = IntField(required=True, help_text="The sum of the quantities for all line items that contribute to the order's current subtotal price.")
    currentSubtotalPriceSet = EmbeddedDocumentField(MoneyBag, required=True, help_text="The sum of the prices for all line items after discounts and returns, in shop and presentment currencies. If taxesIncluded is true, then the subtotal also includes tax.")
    currentTaxLines = ListField(EmbeddedDocumentField(TaxLine), help_text="A list of all tax lines applied to line items on the order, after returns. Tax line prices represent the total price for all tax lines with the same rate and title.")
    currentTotalAdditionalFeesSet = EmbeddedDocumentField(MoneyBag, help_text="The total amount of additional fees after returns, in shop and presentment currencies. Returns null if there are no additional fees for the order.")
    currentTotalDiscountsSet = EmbeddedDocumentField(MoneyBag, required=True, help_text="The total amount discounted on the order after returns, in shop and presentment currencies. This includes both order and line level discounts.")
    currentTotalDutiesSet = EmbeddedDocumentField(MoneyBag, help_text="The total amount of duties after returns, in shop and presentment currencies. Returns null if duties aren't applicable.")
    currentTotalPriceSet = EmbeddedDocumentField(MoneyBag, required=True, help_text="The total price of the order, after returns, in shop and presentment currencies. This includes taxes and discounts.")
    currentTotalTaxSet = EmbeddedDocumentField(MoneyBag, required=True, help_text="The sum of the prices of all tax lines applied to line items on the order, after returns, in shop and presentment currencies.")
    currentTotalWeight = IntField(required=True, help_text="The total weight of the order after returns, in grams.")
    customAttributes = ListField(EmbeddedDocumentField(Attribute), help_text="A list of the custom attributes added to the order.")

    customerAcceptsMarketing = BooleanField(required=True, help_text="Whether the customer agreed to receive marketing materials.")
    # customerJourneySummary = EmbeddedDocumentField(CustomerJourneySummary, help_text="The customer's visits and interactions with the online store before placing the order.")
    customerLocale = StringField(help_text="A two-letter or three-letter language code, optionally followed by a region modifier.")
    discountCode = StringField(help_text="The discount code used for the order.")
    discountCodes = ListField(StringField(), help_text="The discount codes used for the order.")
    displayAddress = ReferenceField(MailingAddress, help_text="The primary address of the customer. Returns null if neither the shipping address nor the billing address was provided.")
    displayFinancialStatus = EnumField(OrderDisplayFinancialStatus, help_text="The financial status of the order that can be shown to the merchant. This field doesn't capture all the details of an order's financial state. It should only be used for display summary purposes.")
    displayFulfillmentStatus = EnumField(OrderDisplayFulfillmentStatus, required=True, help_text="The fulfillment status for the order that can be shown to the merchant. This field does not capture all the details of an order's fulfillment state. It should only be used for display summary purposes. For a more granular view of the fulfillment status, refer to the FulfillmentOrder object.")
    disputes = ListField(LazyReferenceField(OrderDisputeSummary, null=True), required=False, help_text="A list of the disputes associated with the order.")
    edited = BooleanField(required=True, help_text="Whether the order has had any edits applied.")
    email = StringField(help_text="The email address associated with the customer.")
    estimatedTaxes = BooleanField(required=True, help_text="Whether taxes on the order are estimated. This field returns false when taxes on the order are finalized and aren't subject to any changes.")
    fulfillable = BooleanField(required=True, help_text="Whether there are line items that can be fulfilled. This field returns false when the order has no fulfillable line items. For a more granular view of the fulfillment status, refer to the FulfillmentOrder object.")
    # fulfillments = ListField(LazyReferenceField(Fulfillment), required=True, help_text="List of shipments for the order.")
    fullyPaid = BooleanField(required=True, help_text="Whether the order has been paid in full.")
    hasTimelineComment = BooleanField(required=True, help_text="Whether the merchant added a timeline comment to the order.")
    shopify_id = StringField(required=True, unique = True,help_text="A globally-unique ID.")
    legacyResourceId = IntField(required=True, help_text="The ID of the corresponding resource in the REST Admin API.")
    merchantEditable = BooleanField(required=True, help_text="Whether the order can be edited by the merchant. For example, canceled orders can’t be edited.")
    merchantEditableErrors = ListField(StringField(), help_text="A list of reasons why the order can't be edited. For example, 'Canceled orders can't be edited'.")

    # metafield = EmbeddedDocumentField(Metafield, help_text="Returns a metafield by namespace and key that belongs to the resource.")
    name = StringField(required=True, help_text="The unique identifier for the order that appears on the order page in the Shopify admin and the Order status page.")
    netPaymentSet = EmbeddedDocumentField(MoneyBag, required=True, help_text="The net payment for the order, based on the total amount received minus the total amount refunded, in shop and presentment currencies.")
    note = StringField(help_text="The contents of the note associated with the order.")
    originalTotalAdditionalFeesSet = EmbeddedDocumentField(MoneyBag, help_text="The total amount of additional fees after returns, in shop and presentment currencies. Returns null if there are no additional fees for the order.")
    originalTotalDutiesSet = EmbeddedDocumentField(MoneyBag, help_text="The total amount of duties before returns, in shop and presentment currencies. Returns null if duties aren't applicable.")
    originalTotalPriceSet = EmbeddedDocumentField(MoneyBag, required=True, help_text="The total price of the order at the time of order creation, in shop and presentment currencies.")
    paymentCollectionDetails = EmbeddedDocumentField(OrderPaymentCollectionDetails, required=True, help_text="The payment collection details for the order.")
    paymentGatewayNames = ListField(StringField(), help_text="A list of the names of all payment gateways used for the order. For example, 'Shopify Payments' and 'Cash on Delivery (COD)'.")
    paymentTerms = ReferenceField(PaymentTerms, help_text="The payment terms associated with the order.")
    phone = StringField(help_text="The phone number associated with the customer.")
    poNumber = StringField(help_text="The PO number associated with the order.")
    presentmentCurrencyCode = EnumField(CurrencyCode, required=True, help_text="The payment CurrencyCode of the customer for the order.")
    processedAt = DateTimeField(required=True, help_text="The date and time when the order was processed. This date and time might not match the date and time when the order was created.")
    # publication = LazyReferenceField(Publication, help_text="The publication that the order was created from.")
    # purchasingEntity = UnionField([LazyReferenceField(PurchasingEntity)], help_text="The purchasing entity for the order.")
    refundDiscrepancySet = EmbeddedDocumentField(MoneyBag, required=True, help_text="The difference between the suggested and actual refund amount of all refunds that have been applied to the order. A positive value indicates a difference in the merchant's favor, and a negative value indicates a difference in the customer's favor.")
    refundable = BooleanField(required=True, help_text="Whether the order can be refunded.")
    # refunds = ListField(LazyReferenceField(Refund), required=True, help_text="A list of refunds that have been applied to the order.")

    registeredSourceUrl = URLField(help_text="The URL of the source that the order originated from, if found in the domain registry.")
    requiresShipping = BooleanField(required=True, help_text="Whether the order has shipping lines or at least one line item on the order that requires shipping.")
    restockable = BooleanField(required=True, help_text="Whether any line item on the order can be restocked.")
    returnStatus = EnumField(OrderReturnStatus, required=True, help_text="The order's aggregated return status for display purposes.")
    # risk = EmbeddedDocumentField(OrderRiskSummary, required=True, help_text="The risk characteristics for the order.")
    shippingAddress = ReferenceField(MailingAddress, help_text="The mailing address of the customer.")
    shippingLine = ReferenceField(ShippingLine, help_text="A summary of all shipping costs on the order.")
    # shopifyProtect = EmbeddedDocumentField(ShopifyProtectOrderSummary, help_text="The Shopify Protect details for the order. If Shopify Protect is disabled for the shop, then this will be null.")
    sourceIdentifier = StringField(help_text="A unique POS or third party order identifier. For example, '1234-12-1000' or '111-98567-54'. The receipt_number field is derived from this value for POS orders.")
    subtotalLineItemsQuantity = IntField(required=True, help_text="The sum of the quantities for all line items that contribute to the order's subtotal price.")
    subtotalPriceSet = EmbeddedDocumentField(MoneyBag, help_text="The sum of the prices for all line items after discounts and before returns, in shop and presentment currencies. If taxesIncluded is true, then the subtotal also includes tax.")
    # suggestedRefund = Field(SuggestedRefund, help_text="A suggested refund for the order.")
    tags = ListField(StringField(), help_text="A comma separated list of tags associated with the order. Updating tags overwrites any existing tags that were previously added to the order. To add new tags without overwriting existing tags, use the tagsAdd mutation.")
    taxExempt = BooleanField(required=True, help_text="Whether taxes are exempt on the order.")
    taxLines = ListField(EmbeddedDocumentField(TaxLine), help_text="A list of all tax lines applied to line items on the order, before returns. Tax line prices represent the total price for all tax lines with the same rate and title.")
    taxesIncluded = BooleanField(required=True, help_text="Whether taxes are included in the subtotal price of the order.")
    test = BooleanField(required=True, help_text="Whether the order is a test. Test orders are made using the Shopify Bogus Gateway or a payment provider with test mode enabled. A test order can't be converted into a real order and vice versa.")
    totalCapturableSet = EmbeddedDocumentField(MoneyBag, required=True, help_text="The authorized amount that's uncaptured or undercaptured, in shop and presentment currencies. This amount isn't adjusted for returns.")
    totalDiscountsSet = EmbeddedDocumentField(MoneyBag, help_text="The total amount discounted on the order before returns, in shop and presentment currencies. This includes both order and line level discounts.")
    totalOutstandingSet = EmbeddedDocumentField(MoneyBag, required=True, help_text="The total amount not yet transacted for the order, in shop and presentment currencies. A positive value indicates a difference in the merchant's favor (payment from customer to merchant) and a negative value indicates a difference in the customer's favor (refund from merchant to customer).")
    totalPriceSet = EmbeddedDocumentField(MoneyBag, required=True, help_text="The total price of the order, before returns, in shop and presentment currencies. This includes taxes and discounts.")
    totalReceivedSet = EmbeddedDocumentField(MoneyBag, required=True, help_text="The total amount received from the customer before returns, in shop and presentment currencies.")
    totalRefundedSet = EmbeddedDocumentField(MoneyBag, required=True, help_text="The total amount that was refunded, in shop and presentment currencies.")
    totalRefundedShippingSet = EmbeddedDocumentField(MoneyBag, required=True, help_text="The total amount of shipping that was refunded, in shop and presentment currencies.")
    totalShippingPriceSet = EmbeddedDocumentField(MoneyBag, required=True, help_text="The total shipping amount before discounts and returns, in shop and presentment currencies.")
    totalTaxSet = EmbeddedDocumentField(MoneyBag, help_text="The total tax amount before returns, in shop and presentment currencies.")
    totalTipReceivedSet = EmbeddedDocumentField(MoneyBag, required=True, help_text="The sum of all tip amounts for the order, in shop and presentment currencies.")
    totalWeight = IntField(help_text="The total weight of the order before returns, in grams.")
    transactions = ListField(ReferenceField(OrderTransaction), help_text="A list of transactions associated with the order.")
    unpaid = BooleanField(required=True, help_text="Whether no payments have been made for the order.")
    updatedAt = DateTimeField(required=True, help_text="The date and time when the order was modified last.")

    lineitem = ListField(ReferenceField('LineItem'), required=True, help_text="A list of line items in the order.")


# class Order(Document):
#     id = StringField(primary_key=True)
#     billingAddress = EmbeddedDocumentField(CustomerAddress)
#     cancelReason = StringField(
#         choices=[(reason.value, reason.name) for reason in OrderCancelReason],
#         help_text=
#         "The reason for the cancellation of the order. Returns null if the order wasn't canceled."
#     )
#     cancelledAt = DateTimeField()
#     confirmationNumber = StringField()
#     createdAt = DateTimeField(required=True)
#     currencyCode = StringField(required=True,
#                                choices=[code.name for code in CurrencyCode],
#                                help_text="Currency of the money.")
#     customer = LazyReferenceField(
#         'Customer')    # Assuming Customer is defined elsewhere
#     customerLocale = StringField()
#     edited = BooleanField()
#     email = EmailField()
#     financialStatus = StringField(
#         choices=[(status.value, status.name) for status in OrderFinancialStatus
#                 ],
#         help_text="The financial status of the order.")
#     locationName = StringField()
#     name = StringField(required=True)
#     note = StringField()
#     number = IntField(required=True)
#     paymentInformation = EmbeddedDocumentField(OrderPaymentInformation)
#     phone = StringField()
#     poNumber = StringField()
#     processedAt = DateTimeField(required=True)
#     # purchasingEntity = EmbeddedDocumentField(PurchasingEntity)
#     refunds = ListField(EmbeddedDocumentField(Refund))
#     requiresShipping = BooleanField(required=True)
#     shippingAddress = EmbeddedDocumentField(CustomerAddress)
#     shippingDiscountAllocations = ListField(
#         EmbeddedDocumentField(DiscountAllocation))
#     shippingLine = EmbeddedDocumentField(ShippingLine)
#     statusPageUrl = URLField(required=True)
#     subtotal = EmbeddedDocumentField(MoneyV2)
#     totalDuties = EmbeddedDocumentField(MoneyV2)
#     totalPrice = EmbeddedDocumentField(MoneyV2, required=True)
#     totalRefunded = EmbeddedDocumentField(MoneyV2, required=True)
#     totalShipping = EmbeddedDocumentField(MoneyV2, required=True)
#     totalTax = EmbeddedDocumentField(MoneyV2)
#     totalTip = EmbeddedDocumentField(MoneyV2)
#     transactions = ListField(EmbeddedDocumentField(OrderTransaction))






class InventoryLevel(Document):

    # 数据一般不会删除
    # location删除了，location的inventoryLevel也会删除
    # item删除了，item的inventoryLevel也会删除

    quantities = ListField(LazyReferenceField('InventoryQuantity'), required=False)
    location = LazyReferenceField('Location', required=True)
    item = LazyReferenceField('InventoryItem', required=True)

    shopify_id = StringField(required=True, unique=True, help_text="A globally-unique ID.")
    canDeactivate = BooleanField(
        required=True,
        help_text="Whether the inventory level can be deactivated.")
    createdAt = DateTimeField(default=datetime.now, required=True)
    deactivationAlert = StringField()
    updatedAt = DateTimeField(default=datetime.now, required=True)
    available = BooleanField()


    meta = {
        'indexes': [
            'location',    # Assuming you might frequently query by location
            'createdAt'    # Helps in sorting by creation time
        ]
    }


class Location(Document):

    shopify_id = StringField(required=True,unique=True)
    name = StringField(required=True)
    activatable = BooleanField()
    address = EmbeddedDocumentField('LocationAddress')
    addressVerified = BooleanField(required=True)
    # createdAt = DateTimeField(default=datetime.now)
    deactivatable = BooleanField()
    deactivatedAt = DateTimeField()
    deletable = BooleanField()
    fulfillmentService = LazyReferenceField('FulfillmentService')
    fulfillsOnlineOrders = BooleanField()
    hasActiveInventory = BooleanField()
    hasUnfulfilledOrders = BooleanField()

    inventoryLevel = LazyReferenceField('InventoryLevel')
    isActive = BooleanField()
    #isFulfillmentService = BooleanField()
    legacyResourceId = IntField(required=True)
    localPickupSettingsV2 = EmbeddedDocumentField('DeliveryLocalPickupSettings')
    name = StringField(required=True)
    shipsInventory = BooleanField()
    suggestedAddresses = ListField(EmbeddedDocumentField(LocationSuggestedAddress))
    #updatedAt = DateTimeField(default=datetime.now)
