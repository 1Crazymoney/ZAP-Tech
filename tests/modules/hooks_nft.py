#!/usr/bin/python3

from brownie import *
from scripts.deployment import main 

module_source = """
pragma solidity 0.4.25;

contract TestModule {{

    address owner;
    bool hookReturn = true;

    constructor(address _owner) public {{ owner = _owner; }}
    function getOwner() external view returns (address) {{ return owner; }}
    
    function getPermissions()
        external
        pure
        returns
    (
        bytes4[] permissions,
        bytes4[] hooks,
        uint256 hookBools
    )
    {{
        bytes4[] memory _hooks = new bytes4[](1);
        _hooks[0] = {};
        return (permissions, _hooks, uint256(0)-1);
    }}

    function setReturn(bool _return) external {{
        hookReturn = _return;
    }}

    function {}) external returns (bool) {{
        if (!hookReturn) {{
            revert();
        }}
        return true;
    }}

}}"""


def setup():
    main(NFToken)
    global issuer, nft
    nft = NFToken[0]
    issuer = IssuingEntity[0]
    nft.mint(issuer, 100000, 0, "0x00", {'from': a[0]})


def checkTransfer():
    source = '''checkTransfer(
		address[2] _addr,
		bytes32 _authID,
		bytes32[2] _id,
		uint8[2] _rating,
		uint16[2] _country,
		uint256 _value'''
    _hook(nft, nft.checkTransfer, (a[0], a[1], 1000), source, "0x70aaf928")


def checkTransferRange():
    source = '''checkTransferRange(
		address[2] _addr,
		bytes32 _authID,
		bytes32[2] _id,
		uint8[2] _rating,
		uint16[2] _country,
		uint48[2] _range'''
    _hook(nft, nft.checkTransfer, (a[0], a[1], 1000), source, "0x2d79c6d7")


def transferTokenRange(pending=True):
    source = '''transferTokenRange(
		address[2] _addr,
		bytes32[2] _id,
		uint8[2] _rating,
		uint16[2] _country,
		uint48[2] _range'''
    _hook(nft, nft.transfer, (a[1], 1000), source, "0xead529f5")


def token_transferTokensCustodian(skip=True):
    source = '''transferTokensCustodian(
		address _custodian,
		address[2] _addr,
		bytes32[2] _id,
		uint8[2] _rating,
		uint16[2] _country,
		uint256 _value'''
    _hook(token, x, (), source, "0x8b5f1240")


def modifyAuthorizedSupply():
    source = '''modifyAuthorizedSupply(
		address _token,
		uint256 _oldSupply,
		uint256 _newSupply'''
    _hook(nft, nft.modifyAuthorizedSupply, (100000000,), source, "0xb1a1a455")

def totalSupplyChanged_mint():
    source = '''totalSupplyChanged(
		address _addr,
		bytes32 _id,
		uint8 _rating,
		uint16 _country,
		uint256 _old,
		uint256 _new'''
    _hook(nft, nft.mint, (a[2], 1000, 0, "0x00"), source, "0x741b5078")

def totalSupplyChanged_burn():
    source = '''totalSupplyChanged(
		address _addr,
		bytes32 _id,
		uint8 _rating,
		uint16 _country,
		uint256 _old,
		uint256 _new'''
    module = compile_source(module_source.format("0x741b5078", source))[0].deploy(a[0], nft)
    nft.burn(100, 200, {'from': a[0]})
    issuer.attachModule(nft, module, {'from': a[0]})
    nft.burn(300, 400, {'from': a[0]})
    module.setReturn(False, {'from': a[0]})
    check.reverts(nft.burn, (500, 600, {'from': a[0]}))
    issuer.detachModule(nft, module, {'from': a[0]})
    nft.burn(500, 600, {'from': a[0]})



def _hook(contract, fn, args, source, sig):
    args = list(args)+[{'from': a[0]}]
    module = compile_source(module_source.format(sig, source))[0].deploy(a[0], contract)
    fn(*args)
    issuer.attachModule(contract, module, {'from': a[0]})
    fn(*args)
    module.setReturn(False, {'from': a[0]})
    check.reverts(fn, args)
    issuer.detachModule(contract, module, {'from': a[0]})
    fn(*args)