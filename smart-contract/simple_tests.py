# based off https://github.com/algorand/docs/blob/cdf11d48a4b1168752e6ccaf77c8b9e8e599713a/examples/smart_contracts/v2/python/stateful_smart_contracts.py

# This file is meant for students to test their smart contract deployment and interactions

import base64
import unittest
import time

from algosdk.encoding import decode_address, encode_address
from algosdk import transaction
from algosdk import account, mnemonic
from algosdk.v2client import algod
from pyteal import compileTeal, Mode
from election_smart_contract import approval_program, clear_state_program

# fill in your secret mnemonics and algod_headers in secrets.py
from secrets import account_mnemonics, algod_headers, algod_address

from deploy import create_app
from helper import compile_program, wait_for_confirmation, int_to_bytes, read_global_state, read_local_state

account_private_keys = [mnemonic.to_private_key(mn) for mn in account_mnemonics]
account_addresses = [account.address_from_private_key(sk) for sk in account_private_keys]

# algod client
client = algod.AlgodClient(
    algod_token="",
    algod_address=algod_address,
    headers=algod_headers
)


def opt_in_app(client, private_key, index):
    """ OPT IN TO APPLICATION """

    # declare sender
    sender = account.address_from_private_key(private_key)
    print("OptIn from account: ", sender)

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000

    # create unsigned transaction
    txn = transaction.ApplicationOptInTxn(sender, params, index)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    print("OptIn to app-id:", transaction_response["txn"]["txn"]["apid"])


def call_app_approve_voter(client, index, creator_private_key, user_address, yes_or_no_bytes):
    """ CREATOR TO APPROVE VOTER """

    app_args = [b"update_user_status", decode_address(user_address), yes_or_no_bytes]
    # declare sender
    sender = account.address_from_private_key(creator_private_key)

    print("Call from account:", sender)

    # get node suggested parameters
    params = client.suggested_params()

    # create unsigned transaction
    txn = transaction.ApplicationNoOpTxn(sender, params, index, app_args, accounts=[sender, user_address])

    # sign transaction
    signed_txn = txn.sign(creator_private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)
    transaction_response = client.pending_transaction_info(tx_id)
    print("Approved user ", user_address, "for apid ", transaction_response, ": ", yes_or_no_bytes)


def call_app(client, private_key, index, app_args):
    """ CALL APPLICATION """

    # declare sender
    sender = account.address_from_private_key(private_key)
    print("Call from account:", sender)

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000

    # create unsigned transaction
    txn = transaction.ApplicationNoOpTxn(sender, params, index, app_args)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)


def delete_app(client, private_key, index):
    """ DELETE APPLICATION """

    # declare sender
    sender = account.address_from_private_key(private_key)

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000

    # create unsigned transaction
    txn = transaction.ApplicationDeleteTxn(sender, params, index)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    print("Deleted app-id:", transaction_response["txn"]["txn"]["apid"])


def close_out_app(client, private_key, index):
    """ CLOSE OUT FROM APPLICATION """

    # declare sender
    sender = account.address_from_private_key(private_key)

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000

    # create unsigned transaction
    txn = transaction.ApplicationCloseOutTxn(sender, params, index)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    print("Closed out from app-id: ", transaction_response["txn"]["txn"]["apid"])


def clear_state_app(client, private_key, index):
    """ CLEAR STATE OF APPLICATION """

    # declare sender
    sender = account.address_from_private_key(private_key)

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000

    # create unsigned transaction
    txn = transaction.ApplicationClearStateTxn(sender, params, index)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    print("Clear state from app-id: ", transaction_response["txn"]["txn"]["apid"])


def clear_app(client, private_key, index):
    # declare sender
    sender = account.address_from_private_key(private_key)

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000

    # create unsigned transaction
    txn = transaction.ApplicationClearStateTxn(sender, params, index)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    print("Cleared app-id:", transaction_response["txn"]["txn"]["apid"])


def test_create_app(client, creator_private_key, election_end, num_vote_options, vote_options):
    """ TEST CREATION OF APPLICATION """

    # declare application state storage (immutable)
    local_ints = 1  # user's voted variable
    local_bytes = 1  # user's can_vote variable
    global_ints = (
        24  # 3 for setup + x for choices. Use a larger number for more choices.
    )
    global_bytes = 2  # Creator and VoteOptions variables
    global_schema = transaction.StateSchema(global_ints, global_bytes)
    local_schema = transaction.StateSchema(local_ints, local_bytes)

    # get PyTeal approval program
    approval_program_ast = approval_program()
    # compile program to TEAL assembly
    approval_program_teal = compileTeal(
        approval_program_ast, mode=Mode.Application, version=5
    )
    # compile program to binary
    approval_program_compiled = compile_program(client, approval_program_teal)

    # get PyTeal clear state program
    clear_state_program_ast = clear_state_program()
    # compile program to TEAL assembly
    clear_state_program_teal = compileTeal(
        clear_state_program_ast, mode=Mode.Application, version=5
    )
    # compile program to binary
    clear_state_program_compiled = compile_program(
        client, clear_state_program_teal
    )

    # create list of bytes for app args
    app_args = [
        int_to_bytes(election_end),
        int_to_bytes(num_vote_options),
        vote_options
    ]

    # create new application
    app_id = create_app(
        client,
        creator_private_key,
        approval_program_compiled,
        clear_state_program_compiled,
        global_schema,
        local_schema,
        app_args,
    )

    return app_id


class TestSimpleElection(unittest.TestCase):
    """ PROVIDE TESTS FOR BASIC FUNCTIONALITIES """

    def test_01_create_election(self):
        """ tests the creation and initial variable setup """

        print(f"Testing election deployment/creation")

        relative_election_end = 5000
        # app args
        status = client.status()
        election_end = status["last-round"] + relative_election_end
        num_vote_options = 2
        vote_options = "ETH,ALGO"

        # test smart contract creation with large election end time
        TestSimpleElection.app_id = test_create_app(client, account_private_keys[0], election_end, num_vote_options,
                                                    vote_options)
        time.sleep(1.5)

        # check global variables setup
        global_state = read_global_state(client, TestSimpleElection.app_id)
        self.assertEqual(global_state["VoteOptions"], vote_options, "VoteOptions variable is NOT correct")
        self.assertEqual(global_state["ElectionEnd"], election_end, "ElectionEnd variable is NOT correct")
        for i in range(0, 2):
            self.assertEqual(global_state[f"VotesFor{i}"], 0, f"VotesFor{i} not initialized to 0")

    def test_02_opt_in(self):
        """ tests two users opting in to contract """

        # opt-in three users
        for i in range(0, 3):
            print(f"Testing account {account_addresses[i]} opt-in")

            opt_in_app(client, account_private_keys[i], TestSimpleElection.app_id)
            local_state = read_local_state(client, account_addresses[i], TestSimpleElection.app_id)
            self.assertEqual("maybe", local_state["can_vote"], f"User {i}'s can_vote not set to 'maybe'")
            time.sleep(0.5)

            print("-------------------------------------------------------------------------------")

    def test_03_approve_users(self):
        """ tests the "yes" approval of two users """

        # approve the first two users
        for i in range(0, 2):
            print(f"Testing creator approving {account_addresses[i]}")

            # have the creator approve the users with "yes"
            call_app_approve_voter(
                client=client,
                index=TestSimpleElection.app_id,
                creator_private_key=account_private_keys[0],
                user_address=account_addresses[i],
                yes_or_no_bytes=b"yes"
            )
            time.sleep(1)

            # check local state of the user that was approved to ensure it was updated correctly
            local_state = read_local_state(client, account_addresses[i], TestSimpleElection.app_id)
            self.assertEqual("yes", local_state["can_vote"], f"Approved user's can_vote should be 'yes'!")

            print("-------------------------------------------------------------------------------")

    def test_04_voting(self):
        """ tests approved users trying to vote """

        for i in range(0, 2):
            print(f"Testing account {account_addresses[i]} voting for option {i}")

            # have user i vote for option i
            app_args = [b"vote", i.to_bytes(8, 'big')]
            call_app(client, account_private_keys[i], TestSimpleElection.app_id, app_args)
            time.sleep(1)

            # read the local state of the user to ensure it was updated correctly
            local_state = read_local_state(client, account_addresses[i], TestSimpleElection.app_id)
            self.assertEqual(i, local_state["voted"], f"Wrong vote in user's voted variable")
            time.sleep(1)

            # read the global state of app to ensure it was updated correctly
            global_state = read_global_state(client, TestSimpleElection.app_id)
            for j in range(0, 2):
                self.assertEqual(1 if i >= j else 0, global_state[f"VotesFor{j}"])

            print("-------------------------------------------------------------------------------")

    def test_05_unapproved_cant_vote(self):
        """ tests unapproved user trying to vote """

        app_args = [b"vote", (0).to_bytes(8, 'big')]
        # ensure an error occurs when an unapproved user tries to vote
        self.assertRaises(
            Exception,
            call_app,
            client,
            account_private_keys[2],
            TestSimpleElection.app_id,
            app_args
        )

        print("-------------------------------------------------------------------------------")

    def test_06_closeout(self):
        """ test closeout functionality on approved user 1, note: this happens before the election end """

        print(f"Testing close out of account {account_addresses[1]}")
        # close out of the app (note this is happening before the election end)
        close_out_app(client, account_private_keys[1], TestSimpleElection.app_id)
        time.sleep(1)

        # check the global state of the app to make sure values were updated correctly
        global_state = read_global_state(client, TestSimpleElection.app_id)
        self.assertEqual(1, global_state[f"VotesFor{0}"])
        self.assertEqual(0, global_state[f"VotesFor{1}"])  # used to be 1, now is 0

    def test_99_delete_app(self):
        """ delete the app as cleanup to not take up the creator's account's maximum app limit """

        print(f"Deleting app {TestSimpleElection.app_id}")
        delete_app(client, account_private_keys[0], TestSimpleElection.app_id)


if __name__ == '__main__':
    unittest.main()
