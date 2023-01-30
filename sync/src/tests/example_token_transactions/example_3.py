TRANSACTIONS3 = {
    "state_identifier": {
        "state_version": 16477213,
        "transaction_accumulator": "cb03d3831672eaff2bfef07bd3802802a255dd2368407a75b20cb5557866955c"
    },
    "transactions": [
        {
            "transaction_identifier": {
                "hash": "a367b9dfb9561cf12763378bc0f5fe34c7ba557f43f89d6c414c2fcece2014ce"
            },
            "committed_state_identifier": {
                "state_version": 16477214,
                "transaction_accumulator": "2768905ae593ba1d3df21b7fb5ea0b09c272111ebc60434e977865c4fe6f5ee1"
            },
            "operation_groups": [
                {
                    "operations": [
                        {
                            "type": "Data",
                            "entity_identifier": {
                                "address": "system"
                            },
                            "substate": {
                                "substate_operation": "SHUTDOWN",
                                "substate_identifier": {
                                    "identifier": "e3828ef2f65da4085b94eb17b5c80ad8057fda1783cd999bdba800e06c8b06850000012e"
                                }
                            },
                            "data": {
                                "action": "DELETE",
                                "data_object": {
                                    "round": 0,
                                    "timestamp": 1630340710417,
                                    "type": "RoundData"
                                }
                            }
                        },
                        {
                            "type": "Data",
                            "entity_identifier": {
                                "address": "rv1qgrcl8ecx2zzr6kvdytduf3v7t5hntaa05nq7f3jxhfu73360sqjuf82pnu",
                                "sub_entity": {
                                    "address": "system"
                                }
                            },
                            "substate": {
                                "substate_operation": "SHUTDOWN",
                                "substate_identifier": {
                                    "identifier": "e3828ef2f65da4085b94eb17b5c80ad8057fda1783cd999bdba800e06c8b0685000000e3"
                                }
                            },
                            "data": {
                                "action": "DELETE",
                                "data_object": {
                                    "proposals_completed": 0,
                                    "proposals_missed": 0,
                                    "type": "ValidatorBFTData"
                                }
                            }
                        },
                        {
                            "type": "Data",
                            "entity_identifier": {
                                "address": "rv1qgrcl8ecx2zzr6kvdytduf3v7t5hntaa05nq7f3jxhfu73360sqjuf82pnu",
                                "sub_entity": {
                                    "address": "system"
                                }
                            },
                            "substate": {
                                "substate_operation": "BOOTUP",
                                "substate_identifier": {
                                    "identifier": "a367b9dfb9561cf12763378bc0f5fe34c7ba557f43f89d6c414c2fcece2014ce00000000"
                                }
                            },
                            "data": {
                                "action": "CREATE",
                                "data_object": {
                                    "proposals_completed": 1,
                                    "proposals_missed": 0,
                                    "type": "ValidatorBFTData"
                                }
                            }
                        },
                        {
                            "type": "Data",
                            "entity_identifier": {
                                "address": "system"
                            },
                            "substate": {
                                "substate_operation": "BOOTUP",
                                "substate_identifier": {
                                    "identifier": "a367b9dfb9561cf12763378bc0f5fe34c7ba557f43f89d6c414c2fcece2014ce00000001"
                                }
                            },
                            "data": {
                                "action": "CREATE",
                                "data_object": {
                                    "round": 1,
                                    "timestamp": 1630340710548,
                                    "type": "RoundData"
                                }
                            }
                        }
                    ]
                }
            ],
            "metadata": {
                "size": 150,
                "hex": "07e3828ef2f65da4085b94eb17b5c80ad8057fda1783cd999bdba800e06c8b06850000012e07e3828ef2f65da4085b94eb17b5c80ad8057fda1783cd999bdba800e06c8b0685000000e30200330d0002078f9f38328421eacc6916de262cf2e979afbd7d260f263235d3cf463a7c012e00000000000000010000000000000000020012020000000000000000010000017b97e1009400",
                "fee": {
                    "value": "0",
                    "resource_identifier": {
                        "rri": "xrd_rr1qy5wfsfh",
                        "type": "Token"
                    }
                }
            }
        }
    ]
}