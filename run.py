import IPIM

from IPIM.main import app
# from IPIM.main import engine
# from IPIM.database import dbConnect

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.option('--deploy', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, deploy, host, port):
    """
   
    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)

    context = ('ipim.crt', 'ipim.key')

    '''
    if deploy:
        app.config.from_object('IPIM.config.ProductionConfig')
    else:
        app.config.from_object('IPIM.config.Config')

    DATABASEURI = app.config['DATABASE_URI']
    print DATABASEURI
    engine = dbConnect(DATABASEURI)
    '''
	
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded, ssl_context=context)

  run()
