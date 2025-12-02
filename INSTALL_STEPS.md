OPTION A - All in one:
./start_all.sh

OPTION B - OPENWEBUI_CG only:
./openwebui_cg/start_openwebui_cg.sh

OPTION C - LANGBUILDER_CG only:
./langbuilder_cg/start_langbuilder_stack.sh

OPTION D - MANUAL:
Terminal 1: ./openwebui_cg/backend/start_openwebui_simple.sh
Terminal 2: cd openwebui_cg && npm run dev -- --port 5175
Terminal 3: cd langbuilder_cg && make backend
Terminal 4: cd langbuilder_cg && make frontend