//SPDX-License-Identifier: MIT

pragma solidity ^0.8.18;

import {Test, console} from "forge-std/Test.sol";
import {FundMe} from "../../src/FundMe.sol";
import {DeployFundMe} from "../../script/DeployFundMe.s.sol";

contract FundMeTest is Test {
    uint256 number = 1;
    FundMe fundMe;
    // Make fake address that will execute transactions in tests
    address USER = makeAddr("user");
    //decimals don't work
    //in solidity but the unit ether multiplies times 10^8
    uint256 constant SEND_VALUE = 0.1 ether;
    uint256 constant BALANCE = 10 ether;
    uint256 constant GAS_PRICE = 1;

    function setUp() external {
        number = 2;
        DeployFundMe deployFundMe = new DeployFundMe();
        fundMe = deployFundMe.run();
        // give funds to the fake user
        vm.deal(USER, BALANCE);
    }

    function testDemo() public {
        assertEq(number, 2);
    }

    function testMinimumIsFive() public {
        assertEq(fundMe.MINIMUM_USD(), 5e18);
    }

    function testOwnerIsMsgSender() public {
        assertEq(fundMe.i_owner(), msg.sender);
    }

    function testPriceVersion() public {
        uint256 version = fundMe.getVersion();
        assertEq(version, 4);
    }

    function testNotEnoughFunds() public {
        vm.expectRevert();
        fundMe.fund(); // send 0 value
    }

    modifier funded() {
        vm.prank(USER); // the next transaction is done by USER
        fundMe.fund{value: SEND_VALUE}(); // send 0 value
        _;
    }

    function testEnoughFundsansUpdates() public funded {
        uint256 amountFunded = fundMe.getAddressToAmountFunded(USER);
        assertEq(amountFunded, SEND_VALUE);
    }

    function testArrayofFunders() public funded {
        address funder = fundMe.getFunder(0);
        assertEq(funder, USER);
    }

    function testOnlyOwnerCanWithdraw() public funded {
        vm.expectRevert();
        vm.prank(USER);
        fundMe.withdraw();
    }

    function testWithdrawMultipleFunders() public funded {
        //Arange
        uint160 numberFunders = 10;
        uint160 startIndex = 1;
        for (uint160 i = startIndex; i < numberFunders; i++) {
            hoax(address(i), SEND_VALUE); // both prank and deal
            fundMe.fund{value: SEND_VALUE}();
        }

        uint256 startingBalance = fundMe.getOwner().balance;
        uint256 startingFundMeBalance = address(fundMe).balance;

        //Act
        vm.prank(fundMe.getOwner());
        fundMe.withdraw();
        //assert
        uint256 endOwnerBalance = fundMe.getOwner().balance;
        uint256 endFundMeBalance = address(fundMe).balance;
        assertEq(endFundMeBalance, 0);
        assertEq(startingFundMeBalance + startingBalance, endOwnerBalance);
    }

    function testWithdrawSingleFunder() public funded {
        //Aranger
        uint256 startingBalance = fundMe.getOwner().balance;
        uint256 startingFundMeBalance = address(fundMe).balance;

        //Act
        uint256 gasStart = gasleft();
        vm.txGasPrice(GAS_PRICE);
        vm.prank(fundMe.getOwner());
        fundMe.withdraw();
        uint256 gasEnd = gasleft();
        uint256 gasUsed = (gasStart - gasEnd) * tx.gasprice;
        //assert
        uint256 endOwnerBalance = fundMe.getOwner().balance;
        uint256 endFundMeBalance = address(fundMe).balance;
        assertEq(endFundMeBalance, 0);
        assertEq(startingFundMeBalance + startingBalance, endOwnerBalance);
    }
}
