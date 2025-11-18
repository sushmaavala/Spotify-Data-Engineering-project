import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsgluedq.transforms import EvaluateDataQuality

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Default ruleset used by all target nodes with data quality enabled
DEFAULT_DATA_QUALITY_RULESET = """
    Rules = [
        ColumnCount > 0
    ]
"""

# Script generated for node artist
artist_node1763483132179 = glueContext.create_dynamic_frame.from_options(format_options={"quoteChar": "\"", "withHeader": True, "separator": ",", "optimizePerformance": False}, connection_type="s3", format="csv", connection_options={"paths": ["s3://project-spotify-sushma/staging/artists.csv"], "recurse": True}, transformation_ctx="artist_node1763483132179")

# Script generated for node tracks
tracks_node1763483133885 = glueContext.create_dynamic_frame.from_options(format_options={"quoteChar": "\"", "withHeader": True, "separator": ",", "optimizePerformance": False}, connection_type="s3", format="csv", connection_options={"paths": ["s3://project-spotify-sushma/staging/track.csv"], "recurse": True}, transformation_ctx="tracks_node1763483133885")

# Script generated for node album
album_node1763483132788 = glueContext.create_dynamic_frame.from_options(format_options={"quoteChar": "\"", "withHeader": True, "separator": ",", "optimizePerformance": False}, connection_type="s3", format="csv", connection_options={"paths": ["s3://project-spotify-sushma/staging/albums.csv"], "recurse": True}, transformation_ctx="album_node1763483132788")

# Script generated for node Join Album & Artist
JoinAlbumArtist_node1763483321356 = Join.apply(frame1=album_node1763483132788, frame2=artist_node1763483132179, keys1=["artist_id"], keys2=["id"], transformation_ctx="JoinAlbumArtist_node1763483321356")

# Script generated for node Join with tracks
Joinwithtracks_node1763483479390 = Join.apply(frame1=tracks_node1763483133885, frame2=JoinAlbumArtist_node1763483321356, keys1=["track_id"], keys2=["track_id"], transformation_ctx="Joinwithtracks_node1763483479390")

# Script generated for node Drop Fields
DropFields_node1763483572573 = DropFields.apply(frame=Joinwithtracks_node1763483479390, paths=["`.track_id`", "id"], transformation_ctx="DropFields_node1763483572573")

# Script generated for node Destination
EvaluateDataQuality().process_rows(frame=DropFields_node1763483572573, ruleset=DEFAULT_DATA_QUALITY_RULESET, publishing_options={"dataQualityEvaluationContext": "EvaluateDataQuality_node1763483020371", "enableDataQualityResultsPublishing": True}, additional_options={"dataQualityResultsPublishing.strategy": "BEST_EFFORT", "observations.scope": "ALL"})
Destination_node1763483679089 = glueContext.write_dynamic_frame.from_options(frame=DropFields_node1763483572573, connection_type="s3", format="glueparquet", connection_options={"path": "s3://project-spotify-sushma/datawarehouse/", "partitionKeys": []}, format_options={"compression": "snappy"}, transformation_ctx="Destination_node1763483679089")

job.commit()