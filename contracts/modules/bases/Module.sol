pragma solidity 0.4.25;

import "../../bases/MultiSig.sol";

import "../../interfaces/IOrgCode.sol";
import "../../interfaces/IOrgShare.sol";

/**
    @title ModuleBase Abstract Base Contract
    @dev Methods in this ABC are defined in contracts that inherit ModuleBase
*/
contract ModuleBaseABC {
    function getPermissions() external pure returns (bytes4[], bytes4[], uint256);
}


/**
    @title Module Base Contract
    @dev Inherited contract for Custodian modules
*/
contract ModuleBase is ModuleBaseABC {

    bytes32 public ownerID;
    address owner;

    /**
        @notice Base constructor
        @param _owner Contract address that module will be attached to
     */
    constructor(address _owner) public {
        owner = _owner;
        ownerID = MultiSig(_owner).ownerID();
    }

    /** @dev Check that call originates from approved authority, allows multisig */
    function _onlyAuthority() internal returns (bool) {
        return MultiSig(owner).checkMultiSigExternal(
            msg.sender,
            keccak256(msg.data),
            msg.sig
        );
    }

    /**
        @notice Fetch address of org contract that module is active on
        @return Owner contract address
    */
    function getOwner() public view returns (address) {
        return owner;
    }

}


/**
    @title OrgShare Module Base Contract
    @dev Inherited contract for BookShare and CertShare modules
 */
contract OrgShareModuleBase is ModuleBase {

    IOrgShareBase share;
    IOrgCode public org;

    /**
        @notice Base constructor
        @param _share OrgShare contract address
        @param _org OrgCode contract address
     */
    constructor(
        IOrgShareBase _share,
        IOrgCode _org
    )
        public
        ModuleBase(_org)
    {
        org = _org;
        share = _share;
    }

    /** @dev Check that call originates from parent share contract */
    function _onlyShare() internal view {
        require(msg.sender == address(share));
    }

    /**
        @notice Fetch address of share that module is active on
        @return Share address
    */
    function getOwner() public view returns (address) {
        return address(share);
    }

}

/**
    @title BookShare Module Base Contract
    @dev Inherited contract for BookShare modules
 */
contract BookShareModuleBase is OrgShareModuleBase {

    IBookShare public share;

    /**
        @notice Base constructor
        @param _share BookShare contract address
        @param _org OrgCode contract address
     */
    constructor(
        IBookShare _share,
        IOrgCode _org
    )
        public
        OrgShareModuleBase(_share, _org)
    {
        share = _share;
    }

}


/**
    @title CertShare Module Base Contract
    @dev Inherited contract for CertShare modules
 */
contract CertShareModuleBase is OrgShareModuleBase {

    ICertShare public share;

    /**
        @notice Base constructor
        @param _share CertShare contract address
        @param _org OrgCode contract address
     */
    constructor(
        ICertShare _share,
        IOrgCode _org
    )
        public
        OrgShareModuleBase(_share, _org)
    {
        share = _share;
    }

}

contract IssuerModuleBase is ModuleBase {

    IOrgCode public org;
    mapping (address => bool) parents;

    /**
        @notice Base constructor
        @param _org IOrgCode contract address
     */
    constructor(address _org) public ModuleBase(_org) {
        org = IOrgCode(_org);
    }

    /** @dev Check that call originates from share contract */
    function _onlyShare() internal {
        if (!parents[msg.sender]) {
            parents[msg.sender] = org.isActiveOrgShare(msg.sender);
        }
        require (parents[msg.sender]);
    }

}
