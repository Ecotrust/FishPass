#!/bin/bash

PYTHON="/usr/local/apps/marineplanner-core/env/bin/python"
MANAGE="/usr/local/apps/marineplanner-core/marineplanner/manage.py"
IMPORT="import_focus_areas"
LOAD="loaddata"
LYR_DIR="/usr/local/apps/marineplanner-core/apps/FishPass/layers/updated_Feb_2019"

echo "Deleting existing Focus Area Records..."
$PYTHON $MANAGE empty_focus_areas

echo "Importing HUC02 records..."
$PYTHON $MANAGE $IMPORT $LYR_DIR/FP_HUC2_complex.zip HUC02
echo "Importing HUC04 records..."
$PYTHON $MANAGE $IMPORT $LYR_DIR/FP_HUC4_complex.zip HUC04
echo "Importing HUC06 records..."
$PYTHON $MANAGE $IMPORT $LYR_DIR/FP_HUC6_complex.zip HUC06

echo "Importing HUC08 records (from fixture)..."
$PYTHON $MANAGE $LOAD $LYR_DIR/FP_HUC8_complex.json
echo "Importing HUC10 records (from fixture)..."
$PYTHON $MANAGE $LOAD $LYR_DIR/FP_HUC10_complex.json
echo "Importing HUC12 records (simplified, from fixture)..."
$PYTHON $MANAGE $LOAD $LYR_DIR/FP_HUC12_simple.json

echo "Importing County records..."
$PYTHON $MANAGE $IMPORT $LYR_DIR/FP_County_complex.zip County
echo "Importing Region records..."
$PYTHON $MANAGE $IMPORT $LYR_DIR/FP_Region_complex.zip Region
echo "Importing Extent records..."
$PYTHON $MANAGE $IMPORT $LYR_DIR/FP_Extent_complex.zip Boundary
echo "Importing Coho records..."
$PYTHON $MANAGE $IMPORT $LYR_DIR/ED_Coho_complex.zip Coho
echo "Importing Chinook records..."
$PYTHON $MANAGE $IMPORT $LYR_DIR/ED_Chinook_complex.zip Chinook
echo "Importing Spring Chinook records..."
$PYTHON $MANAGE $IMPORT $LYR_DIR/ED_Chinook_Spring_complex.zip Chinook_Spring
echo "Importing Fall Chinook records..."
$PYTHON $MANAGE $IMPORT $LYR_DIR/ED_Chinook_Fall_complex.zip Chinook_Fall
echo "Importing Steelhead records..."
$PYTHON $MANAGE $IMPORT $LYR_DIR/ED_Steelhead_complex.zip Steelhead
echo "Done importing Focus Area records"
