import SocketServer
import logging
import socket

import sys
from tatsu.exceptions import ParseException
from tatsu.semantics import ModelBuilderSemantics

from response import Response
from lang.parser import DatavaultLanguageParser
from lang.walker import DatavaultLangWalker
from lang.no_kw_str import NoKwStr
from lang.commands import Exit


class ConnectionHandler(SocketServer.BaseRequestHandler):
    def __init__(self, request, client_address, server):
        logging.debug('Got a new request, handling it')
        self.parser = DatavaultLanguageParser()
        self.walker = DatavaultLangWalker()
        self.vault = server.vault
        SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)

    def handle(self):
        # todo - this may not read the entire data
        command = self.request.recv(2048)
        logging.debug('Received new command: %s', repr(command))

        try:
            self.vault.backup()
        except:
            logging.error('Unable to backup!')

        try:
            parsed_cmd = self.parser.parse(command, 'prog', semantics=ModelBuilderSemantics(
                types=[NoKwStr]
            ))
        except ParseException as e:
            logging.error('Parsing of incoming command failed.')
            self.request.sendall(Response('FAILED').to_json())
            return
        else:
            self.walker.walk(parsed_cmd)

            results = []
            exit_flag = False
            for cmd in self.walker.program_info.commands:
                logging.debug('Processing a command: %s', cmd.__class__.__name__)
                r = self.vault.command_process(self.walker.program_info, cmd)
                results.append(r)
                if isinstance(command, Exit):
                    results.append(r)
                    exit_flag = True
                    break

                if r.status == 'FAILED' or r.status == 'DENIED':
                    try:
                        logging.debug('Command has failed, restoring from backup.')
                        self.vault.restore()
                    except:
                        logging.exception('Unable to restore from a backup!')
                    # remove all previous results
                    results = [r]
                    break

            final_response = ''
            for r in results:
                final_response += '{}\n'.format(r.to_json())
            self.request.sendall(final_response)

            if exit_flag:
                self.vault.stop()
                sys.exit(0)

            for item in self.vault.item_store.keys():

                if self.vault.item_store[item].scope == "local":
                    del self.vault.item_store[item]


class VaultServer(SocketServer.TCPServer):
    def __init__(self, server_address, vault, RequestHandlerClass):
        self.vault = vault
        SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass)

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.settimeout(10)
        self.socket.bind(self.server_address)
