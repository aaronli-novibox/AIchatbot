register_schema = {
    'tags': ['User Management'],
    'parameters': [
        {
            'name': 'email',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'User\'s email address',
            'example': 'john.doe@example.com'
        },
        {
            'name': 'password',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'User\'s password',
            'example': 'password123'
        },
        {
            'name': 'firstName',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'User\'s first name',
            'example': 'John'
        },
        {
            'name': 'lastName',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'User\'s last name',
            'example': 'Doe'
        },
        {
            'name': 'middleName',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'description': 'User\'s middle name',
            'example': 'M'
        },
        {
            'name': 'username',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'User\'s username',
            'example': 'johndoe'
        },
        {
            'name': 'promoCode',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'description': 'User\'s promo code',
            'example': 'PROMO123'
        },
        {
            'name': 'age',
            'in': 'formData',
            'type': 'integer',
            'required': False,
            'description': 'User\'s age',
            'example': 25
        },
        {
            'name': 'country',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'description': 'User\'s country',
            'example': 'USA'
        },
        {
            'name': 'state',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'description': 'User\'s state',
            'example': 'NY'
        },
        {
            'name': 'city',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'description': 'User\'s city',
            'example': 'New York'
        },
        {
            'name': 'zipcode',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'description': 'User\'s zipcode',
            'example': '10001'
        },
        {
            'name': 'shippingAddress',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'description': 'User\'s shipping address',
            'example': '1234 Main St, Apt 101, New York, NY 10001'
        },
        {
            'name': 'phone',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'description': 'User\'s phone number',
            'example': '+1234567890'
        },
        {
            'name': 'bio',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'description': 'User\'s biography',
            'example': 'Social media influencer with a passion for fashion and beauty.'
        },
        {
            'name': 'collaborations',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'description': 'User\'s collaborations in JSON format',
            'example': '[{"brand": "Brand A", "campaign": "Summer Collection"}]'
        },
        {
            'name': 'niches',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'description': 'User\'s niches in JSON format',
            'example': '[{"category": "Fashion"}, {"category": "Beauty"}]'
        },
        {
            'name': 'interests',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'description': 'User\'s interests in JSON format',
            'example': '[{"interest": "Makeup"}, {"interest": "Travel"}]'
        },
        {
            'name': 'audience',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'description': 'User\'s audience in JSON format',
            'example': '[{"age_group": "18-24", "location": "USA"}]'
        },
        {
            'name': 'avatar',
            'in': 'formData',
            'type': 'file',
            'required': False,
            'description': 'User\'s avatar file'
        }
    ],
    'responses': {
        '201': {
            'description': 'Registration successful',
            'examples': {
                'application/json': {
                    'message': 'Registration successful'
                }
            }
        },
        '200': {
            'description': 'Registration successful (no email sent)',
            'examples': {
                'application/json': {
                    'message': 'Registration successful'
                }
            }
        },
        '409': {
            'description': 'Email already in use',
            'examples': {
                'application/json': {
                    'error': 'Email already in use'
                }
            }
        },
        '500': {
            'description': 'Email sending failed',
            'examples': {
                'application/json': {
                    'message': 'Email sending failed'
                }
            }
        }
    }
}

login_schema = {
    'tags': ['User Management'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['password'],
                'properties': {
                    'email': {
                        'type': 'string',
                        'description': 'Email of the influencer',
                        'example': 'john.doe@example.com'
                    },
                    'promocode': {
                        'type': 'string',
                        'description': 'Promocode of the influencer',
                        'example': 'PROMO123'
                    },
                    'password': {
                        'type': 'string',
                        'description': 'Password of the influencer',
                        'example': 'password123'
                    }
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Login successful',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': 'Login successful'
                    },
                    'user': {
                        'type': 'object',
                        'properties': {
                            'influencer_name': {'type': 'string', 'example': 'john_doe'},
                            'influencer_email': {'type': 'string', 'example': 'john.doe@example.com'},
                            'promo_code': {'type': 'string', 'example': 'PROMO123'},
                            'first_name': {'type': 'string', 'example': 'John'},
                            'last_name': {'type': 'string', 'example': 'Doe'},
                            'middle_name': {'type': 'string', 'example': 'M'},
                            'age': {'type': 'integer', 'example': 25},
                            'country': {'type': 'string', 'example': 'USA'},
                            'state': {'type': 'string', 'example': 'NY'},
                            'city': {'type': 'string', 'example': 'New York'},
                            'zipcode': {'type': 'string', 'example': '10001'},
                            'shipping_address': {'type': 'string', 'example': '1234 Main St, Apt 101, New York, NY 10001'},
                            'phone': {'type': 'string', 'example': '+1234567890'},
                            'bio': {'type': 'string', 'example': 'Social media influencer with a passion for fashion and beauty.'},
                            'collaboration': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'brand': {'type': 'string', 'example': 'Brand A'},
                                        'campaign': {'type': 'string', 'example': 'Summer Collection'}
                                    }
                                }
                            },
                            'audience': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'age_group': {'type': 'string', 'example': '18-24'},
                                        'location': {'type': 'string', 'example': 'USA'}
                                    }
                                }
                            },
                            'niche': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'category': {'type': 'string', 'example': 'Fashion'}
                                    }
                                }
                            },
                            'interest': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'interest': {'type': 'string', 'example': 'Makeup'}
                                    }
                                }
                            },
                            'is_email_confirmed': {'type': 'boolean', 'example': True}
                        }
                    },
                    'token': {'type': 'string', 'example': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjA1Y2ZjODVjMTJmNzYwMDAxZjA0ZTI1IiwiZXhwIjoxNjIxMzIzMTUyfQ.5GVBTBx3y3WgJmL4Iepw6_GcMdK-0dQ9p7GfqyBfQzI'}
                }
            }
        },
        '400': {
            'description': 'Email not confirmed',
            'examples': {
                'application/json': {
                    'error': 'Email not confirmed'
                }
            }
        },
        '401': {
            'description': 'Invalid password',
            'examples': {
                'application/json': {
                    'error': 'Invalid password'
                }
            }
        },
        '404': {
            'description': 'Email or promocode not found',
            'examples': {
                'application/json': {
                    'error': 'Email or promocode not found'
                }
            }
        },
        '415': {
            'description': 'Please use Promo Code to log',
            'examples': {
                'application/json': {
                    'error': 'Please use Promo Code to log'
                }
            }
        }
    }
}

check_username_schema = {
    'tags': ['User Management'],
    'parameters': [
        {
            'name': 'username',
            'in': 'body',
            'type': 'string',
            'required': True,
            'description': 'Username to check for uniqueness',
            'example': 'johndoe'
        }
    ],
    'responses': {
        '200': {
            'description': 'Username check result',
            'examples': {
                'application/json': {
                    'isUnique': True
                }
            }
        }
    }
}

check_email_schema = {
    'tags': ['User Management'],
    'parameters': [
        {
            'name': 'email',
            'in': 'body',
            'type': 'string',
            'required': True,
            'description': 'Email to check for uniqueness',
            'example': 'john.doe@example.com'
        }
    ],
    'responses': {
        '200': {
            'description': 'Email check result',
            'examples': {
                'application/json': {
                    'isUnique': True
                }
            }
        }
    }
}

promo_generator_schema = {
    'tags': ['User Management'],
    'parameters': [
        {
            'name': 'firstname',
            'in': 'body',
            'type': 'string',
            'required': True,
            'description': 'User\'s first name',
            'example': 'John'
        },
        {
            'name': 'lastname',
            'in': 'body',
            'type': 'string',
            'required': True,
            'description': 'User\'s last name',
            'example': 'Doe'
        }
    ],
    'responses': {
        '200': {
            'description': 'Promo code generated',
            'examples': {
                'application/json': {
                    'message': 'Generate successful',
                    'promocode': 'DO_J_NOVIBOX_1'
                }
            }
        }
    }
}

check_promo_schema = {
    'tags': ['User Management'],
    'parameters': [
        {
            'name': 'promocode',
            'in': 'body',
            'type': 'string',
            'required': True,
            'description': 'Promo code to check for uniqueness',
            'example': 'DO_J_NOVIBOX_1'
        }
    ],
    'responses': {
        '200': {
            'description': 'Promo code check result',
            'examples': {
                'application/json': {
                    'isUnique': True
                }
            }
        }
    }
}

get_userbroad_schema = {
    'tags': ['User Dashboard'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['influencer_name', 'range', 'month'],
                'properties': {
                    'influencer_name': {
                        'type': 'string',
                        'description': 'Name of the influencer',
                        'example': 'john_doe'
                    },
                    'range': {
                        'type': 'array',
                        'items': {
                            'type': 'string',
                            'example': '2023-05'
                        },
                        'description': 'Range of months to get top products'
                    },
                    'month': {
                        'type': 'string',
                        'description': 'Month to get the last month statistics',
                        'example': '2023-05'
                    }
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Dashboard data retrieved successfully',
            'examples': {
                'application/json': {
                    'cards': {
                        'total_earnings': 5000,
                        'last_month_earning': 1000,
                        'last_month_sold_products': 50
                    },
                    'top_products': [
                        {'2023-05': [
                            {'product_id': '123', 'name': 'Product 1', 'sales': 10},
                            {'product_id': '124', 'name': 'Product 2', 'sales': 8}
                        ]}
                    ]
                }
            }
        },
        '400': {
            'description': 'Missing influencer name',
            'examples': {
                'application/json': {
                    'message': 'Influencer name is required'
                }
            }
        },
        '404': {
            'description': 'Influencer not found',
            'examples': {
                'application/json': {
                    'error': 'Influencer not found'
                }
            }
        }
    }
}

forgot_password_schema = {
    'tags': ['User Management'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['email'],
                'properties': {
                    'email': {
                        'type': 'string',
                        'description': 'Email of the influencer',
                        'example': 'john.doe@example.com'
                    }
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Email sent successfully',
            'examples': {
                'application/json': {
                    'message': 'Email Sent'
                }
            }
        },
        '404': {
            'description': 'User not found',
            'examples': {
                'application/json': {
                    'error': 'User not found'
                }
            }
        },
        '415': {
            'description': 'Please contact the administrator to change the password!',
            'examples': {
                'application/json': {
                    'error': 'Please contact the administrator to change the password!'
                }
            }
        },
        '500': {
            'description': 'Email sending failed',
            'examples': {
                'application/json': {
                    'message': 'Email sending failed'
                }
            }
        }
    }
}

reset_with_token_schema = {
    'tags': ['User Management'],
    'parameters': [
        {
            'name': 'token',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'Token for password reset',
            'example': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['password'],
                'properties': {
                    'password': {
                        'type': 'string',
                        'description': 'New password for the influencer',
                        'example': 'newpassword123'
                    }
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Password reset successfully',
            'examples': {
                'application/json': {
                    'message': 'Password reset successfully'
                }
            }
        },
        '400': {
            'description': 'Token expired',
            'examples': {
                'application/json': {
                    'message': 'Token Expired'
                }
            }
        }
    }
}

get_all_products_schema = {
    'tags': ['Product Management'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['influencer_name', 'role'],
                'properties': {
                    'influencer_name': {
                        'type': 'string',
                        'description': 'Name of the influencer',
                        'example': 'john_doe'
                    },
                    'role': {
                        'type': 'string',
                        'description': 'Role of the user',
                        'example': 'admin'
                    },
                    'search': {
                        'type': 'string',
                        'description': 'Search term for filtering products',
                        'example': 'summer'
                    }
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Successfully returns the list of products',
            'examples': {
                'application/json': {
                    'products': [
                        {
                            'title': 'Summer Collection T-Shirt',
                            'commission_rate': 10,
                            'status': True,
                            'start_time': '2023-01-01',
                            'end_time': '2023-12-31',
                            'video_exposure': 5000,
                            'product_shopify_id': '123456',
                            'featuredImage': 'http://example.com/image.jpg',
                            'onlineStoreUrl': 'http://example.com/store'
                        }
                    ]
                }
            }
        }
    }
}

get_influencer_products_schema = {
    'tags': ['Products'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['influencer_name', 'role'],
                'properties': {
                    'influencer_name': {
                        'type': 'string',
                        'description': 'Name of the influencer',
                        'example': 'john_doe'
                    },
                    'search': {
                        'type': 'string',
                        'description': 'Search term for filtering products',
                        'example': 't-shirt'
                    }
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Products retrieved successfully',
            'examples': {
                'application/json': {
                    'products': [
                        {
                            'id': '609b8a8e8e9f1b001f8b4567',
                            'name': 'Product 1',
                            'description': 'Description of product 1',
                            'price': 29.99
                        },
                        {
                            'id': '609b8a8e8e9f1b001f8b4568',
                            'name': 'Product 2',
                            'description': 'Description of product 2',
                            'price': 49.99
                        }
                    ]
                }
            }
        },
        '400': {
            'description': 'Influencer name is required',
            'examples': {
                'application/json': {
                    'message': 'Influencer name is required'
                }
            }
        },
        '404': {
            'description': 'Influencer not found',
            'examples': {
                'application/json': {
                    'message': 'Influencer not found'
                }
            }
        }
    }
}

get_bd_influencers_products_schema = {
    'tags': ['Products'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['influencer_name', 'role'],
                'properties': {
                    'influencer_name': {
                        'type': 'string',
                        'description': 'Name of the influencer',
                        'example': 'john_doe'
                    },
                    'search': {
                        'type': 'string',
                        'description': 'Search term for filtering products',
                        'example': 't-shirt'
                    },
                    'role': {
                        'type': 'string',
                        'description': 'Role of the user',
                        'example': 'admin'
                    }
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'All influencer products retrieved successfully',
            'examples': {
                'application/json': {
                    'products': [
                        {
                            'id': '609b8a8e8e9f1b001f8b4567',
                            'name': 'Product 1',
                            'description': 'Description of product 1',
                            'price': 29.99
                        },
                        {
                            'id': '609b8a8e8e9f1b001f8b4568',
                            'name': 'Product 2',
                            'description': 'Description of product 2',
                            'price': 49.99
                        }
                    ]
                }
            }
        },
        '400': {
            'description': 'Role name is required',
            'examples': {
                'application/json': {
                    'message': 'Role name is required'
                }
            }
        }
    }
}

get_orderlist_schema = {
    'tags': ['Orders'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['influencer_name'],
                'properties': {
                    'influencer_name': {
                        'type': 'string',
                        'description': 'Name of the influencer',
                        'example': 'john_doe'
                    },
                    'search': {
                        'type': 'string',
                        'description': 'Search term for filtering orders',
                        'example': 'order123'
                    }
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Orders retrieved successfully',
            'examples': {
                'application/json': {
                    'orders': [
                        {
                            'order_id': 'order123',
                            'product_id': '609b8a8e8e9f1b001f8b4567',
                            'quantity': 2,
                            'total_price': 59.98
                        },
                        {
                            'order_id': 'order124',
                            'product_id': '609b8a8e8e9f1b001f8b4568',
                            'quantity': 1,
                            'total_price': 49.99
                        }
                    ]
                }
            }
        },
        '404': {
            'description': 'Influencer not found',
            'examples': {
                'application/json': {
                    'message': 'Influencer not found'
                }
            }
        }
    }
}

get_all_orderlist_schema = {
    'tags': ['Orders'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['role'],
                'properties': {
                    'role': {
                        'type': 'string',
                        'description': 'Role of the user',
                        'example': 'admin'
                    },
                    'search': {
                        'type': 'string',
                        'description': 'Search term for filtering orders',
                        'example': 'order123'
                    }
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'All orders retrieved successfully',
            'examples': {
                'application/json': {
                    'orders': []
                }
            }
        },
        '404': {
            'description': 'Influencer not found',
            'examples': {
                'application/json': {
                    'message': 'Influencer not found'
                }
            }
        }
    }
}

get_influencerlist_schema = {
    'tags': ['Influencers'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['role'],
                'properties': {
                    'search': {
                        'type': 'string',
                        'description': 'Search term for filtering influencers',
                        'example': 'fashion'
                    },
                    'role': {
                        'type': 'string',
                        'description': 'Role of the user',
                        'example': 'admin'
                    }
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Influencers retrieved successfully',
            'examples': {
                'application/json': {
                    'influencers': [
                        {
                            'influencer_name': 'john_doe',
                            'email': 'john.doe@example.com',
                            'avatar': 'base64encodedavatarstring==',
                            'bio': 'Fashion influencer with 100k followers',
                            'country': 'USA'
                        },
                        {
                            'influencer_name': 'jane_doe',
                            'email': 'jane.doe@example.com',
                            'avatar': 'base64encodedavatarstring==',
                            'bio': 'Beauty influencer with 200k followers',
                            'country': 'Canada'
                        }
                    ]
                }
            }
        },
        '200_alt': {
            'description': 'Not an admin account',
            'examples': {
                'application/json': {
                    'msg': 'Not admin account'
                }
            }
        }
    }
}

get_influencer_info_schema = {
    'tags': ['Influencers'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['influencer_name'],
                'properties': {
                    'influencer_name': {
                        'type': 'string',
                        'description': 'Name of the influencer',
                        'example': 'john_doe'
                    }
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Influencer information retrieved successfully',
            'examples': {
                'application/json': {
                    'data': {
                        'influencer_name': 'john_doe',
                        'email': 'john.doe@example.com',
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'avatar': 'base64encodedavatarstring==',
                        'bio': 'Fashion influencer with 100k followers',
                        'country': 'USA',
                        'state': 'NY',
                        'city': 'New York',
                        'zipcode': '10001',
                        'shipping_address': '1234 Main St, Apt 101, New York, NY 10001',
                        'phone': '+1234567890',
                        'collaboration': [
                            {'brand': 'Brand A', 'campaign': 'Summer Collection'}
                        ],
                        'audience': [
                            {'age_group': '18-24', 'location': 'USA'}
                        ],
                        'niche': [
                            {'category': 'Fashion'}
                        ],
                        'interest': [
                            {'interest': 'Makeup'}
                        ]
                    }
                }
            }
        },
        '404': {
            'description': 'Influencer not found',
            'examples': {
                'application/json': {
                    'message': 'Influencer not found'
                }
            }
        }
    }
}
