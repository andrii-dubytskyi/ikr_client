import sys

print(sys.argv)
if len(sys.argv) > 1 and sys.argv[1] == 'config':
    import config
    config.configure()
else:
    import ikr_client
    ikr_client.main()
