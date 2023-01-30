TRANSACTIONS2 = {
    "state_identifier": {
        "state_version": 40897,
        "transaction_accumulator": "dd61e3e2c9cdda8bf8973ea7d6dd4e6482c569fff45f0ca5e2bfd196f5bae4c9"
    },
    "transactions": [
        {
            "metadata": {
                "size": 360,
                "signed_by": {
                    "hex": "02aa1c49af92a39d15257d7dc43f805f18f9f0ea712450c53e75255f5a0d1d93b6"
                },
                "fee": {
                    "resource": {
                        "rri": "xrd_rr1qy5wfsfh",
                        "type": "Token"
                    },
                    "value": "72000000000000000"
                },
                "hex": "07030e7094728c8d065c5db696977696bea9094f67bcfd4c021f99ec784e24023b0000000c0100210000000000000000000000000000000000000000000000000000ffcb9e57d4000002004506000402aa1c49af92a39d15257d7dc43f805f18f9f0ea712450c53e75255f5a0d1d93b601000000000000000000000000000000000000000007c13bc4b1c16827082c00000008000002004506000402aa1c49af92a39d15257d7dc43f805f18f9f0ea712450c53e75255f5a0d1d93b601000000000000000000000000000000000000000007ad6192165e31dff02c000002004506000403dc62fa04804f75d009a2fac32c8ceb9dc5eaccd54934fe20ef5b86be40c7a2ab0100000000000000000000000000000000000000000013da329b63364718000000000b015584aed8375f30b22a2203b77dbe15e5dc0a3618fb45ea30ee54a6ebe0054b673a471ad2214b7bd06c4228083643b57e095787c9fb01443e1c3d6890d28f60cf",
                "timestamp": 1627407310726
            },
            "committed_state_identifier": {
                "state_version": 40898,
                "transaction_accumulator": "5ea573f2e31640d177047d14122f1015c262f0d14d522596068784406aa1d88f"
            },
            "transaction_identifier": {
                "hash": "ef71a9d6c63444fce6abd2df8fab2755cfb51f6794e578f60d99337193811842"
            },
            "operation_groups": [
                {
                    "metadata": {
                        "action": {
                            "amount": "72000000000000000",
                            "rri": "xrd_rr1qy5wfsfh",
                            "from": "rdx1qsp258zf47f288g4y47hm3plsp03370safcjg5x98e6j2h66p5we8ds8m7g33",
                            "type": "BurnTokens"
                        }
                    },
                    "operations": [
                        {
                            "amount": {
                                "resource_identifier": {
                                    "rri": "xrd_rr1qy5wfsfh",
                                    "type": "Token"
                                },
                                "value": "-2400000000000000000000000000"
                            },
                            "substate": {
                                "substate_identifier": {
                                    "identifier": "030e7094728c8d065c5db696977696bea9094f67bcfd4c021f99ec784e24023b0000000c"
                                },
                                "substate_operation": "SHUTDOWN"
                            },
                            "entity_identifier": {
                                "address": "rdx1qsp258zf47f288g4y47hm3plsp03370safcjg5x98e6j2h66p5we8ds8m7g33"
                            },
                            "type": "Resource"
                        },
                        {
                            "metadata": {
                                "substate_data_hex": "06000402aa1c49af92a39d15257d7dc43f805f18f9f0ea712450c53e75255f5a0d1d93b601000000000000000000000000000000000000000007c13bc4b1c16827082c0000"
                            },
                            "amount": {
                                "resource_identifier": {
                                    "rri": "xrd_rr1qy5wfsfh",
                                    "type": "Token"
                                },
                                "value": "2399999999928000000000000000"
                            },
                            "substate": {
                                "substate_identifier": {
                                    "identifier": "ef71a9d6c63444fce6abd2df8fab2755cfb51f6794e578f60d9933719381184200000000"
                                },
                                "substate_operation": "BOOTUP"
                            },
                            "entity_identifier": {
                                "address": "rdx1qsp258zf47f288g4y47hm3plsp03370safcjg5x98e6j2h66p5we8ds8m7g33"
                            },
                            "type": "Resource"
                        }
                    ]
                },
                {
                    "metadata": {
                        "action": {
                            "amount": "24000000000000000000000000",
                            "rri": "xrd_rr1qy5wfsfh",
                            "from": "rdx1qsp258zf47f288g4y47hm3plsp03370safcjg5x98e6j2h66p5we8ds8m7g33",
                            "to": "rdx1qspacch6qjqy7awspx304sev3n4em302en25jd87yrh4hp47grr692cm0kv88",
                            "type": "TokenTransfer"
                        }
                    },
                    "operations": [
                        {
                            "amount": {
                                "resource_identifier": {
                                    "rri": "xrd_rr1qy5wfsfh",
                                    "type": "Token"
                                },
                                "value": "-2399999999928000000000000000"
                            },
                            "substate": {
                                "substate_identifier": {
                                    "identifier": "ef71a9d6c63444fce6abd2df8fab2755cfb51f6794e578f60d9933719381184200000000"
                                },
                                "substate_operation": "SHUTDOWN"
                            },
                            "entity_identifier": {
                                "address": "rdx1qsp258zf47f288g4y47hm3plsp03370safcjg5x98e6j2h66p5we8ds8m7g33"
                            },
                            "type": "Resource"
                        },
                        {
                            "metadata": {
                                "substate_data_hex": "06000402aa1c49af92a39d15257d7dc43f805f18f9f0ea712450c53e75255f5a0d1d93b601000000000000000000000000000000000000000007ad6192165e31dff02c0000"
                            },
                            "amount": {
                                "resource_identifier": {
                                    "rri": "xrd_rr1qy5wfsfh",
                                    "type": "Token"
                                },
                                "value": "2375999999928000000000000000"
                            },
                            "substate": {
                                "substate_identifier": {
                                    "identifier": "ef71a9d6c63444fce6abd2df8fab2755cfb51f6794e578f60d9933719381184200000001"
                                },
                                "substate_operation": "BOOTUP"
                            },
                            "entity_identifier": {
                                "address": "rdx1qsp258zf47f288g4y47hm3plsp03370safcjg5x98e6j2h66p5we8ds8m7g33"
                            },
                            "type": "Resource"
                        },
                        {
                            "metadata": {
                                "substate_data_hex": "06000403dc62fa04804f75d009a2fac32c8ceb9dc5eaccd54934fe20ef5b86be40c7a2ab0100000000000000000000000000000000000000000013da329b63364718000000"
                            },
                            "amount": {
                                "resource_identifier": {
                                    "rri": "xrd_rr1qy5wfsfh",
                                    "type": "Token"
                                },
                                "value": "24000000000000000000000000"
                            },
                            "substate": {
                                "substate_identifier": {
                                    "identifier": "ef71a9d6c63444fce6abd2df8fab2755cfb51f6794e578f60d9933719381184200000002"
                                },
                                "substate_operation": "BOOTUP"
                            },
                            "entity_identifier": {
                                "address": "rdx1qspacch6qjqy7awspx304sev3n4em302en25jd87yrh4hp47grr692cm0kv88"
                            },
                            "type": "Resource"
                        }
                    ]
                }
            ]
        }
    ]
}
