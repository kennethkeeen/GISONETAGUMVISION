from django.core.management.base import BaseCommand
from projeng.clustering_comparison import run_clustering_comparison
from projeng.models import ClusteringAlgorithmComparison


class Command(BaseCommand):
    help = 'Compare clustering algorithms (Administrative, K-Means, DBSCAN, Hierarchical)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Clustering Algorithm Comparison...'))
        
        try:
            # Run comparison
            comparison_data = run_clustering_comparison()
            
            # Save to database
            results = comparison_data['results']
            
            comparison = ClusteringAlgorithmComparison.objects.create(
                total_projects=comparison_data['total_projects'],
                valid_projects=comparison_data['valid_projects'],
                best_algorithm=comparison_data['best_algorithm'],
                # Administrative
                admin_silhouette=results['administrative']['metrics']['silhouette_score'],
                admin_zas=results['administrative']['metrics']['zoning_alignment_score'],
                admin_calinski=results['administrative']['metrics']['calinski_harabasz_score'],
                admin_davies=results['administrative']['metrics']['davies_bouldin_score'],
                admin_execution_time=results['administrative']['metrics']['execution_time'],
                admin_cluster_count=results['administrative']['metrics']['cluster_count'],
                # K-Means
                kmeans_silhouette=results['kmeans']['metrics']['silhouette_score'],
                kmeans_zas=results['kmeans']['metrics']['zoning_alignment_score'],
                kmeans_calinski=results['kmeans']['metrics']['calinski_harabasz_score'],
                kmeans_davies=results['kmeans']['metrics']['davies_bouldin_score'],
                kmeans_execution_time=results['kmeans']['metrics']['execution_time'],
                kmeans_cluster_count=results['kmeans']['metrics']['cluster_count'],
                # DBSCAN
                dbscan_silhouette=results['dbscan']['metrics']['silhouette_score'],
                dbscan_zas=results['dbscan']['metrics']['zoning_alignment_score'],
                dbscan_calinski=results['dbscan']['metrics']['calinski_harabasz_score'],
                dbscan_davies=results['dbscan']['metrics']['davies_bouldin_score'],
                dbscan_execution_time=results['dbscan']['metrics']['execution_time'],
                dbscan_cluster_count=results['dbscan']['metrics']['cluster_count'],
                dbscan_noise_count=results['dbscan']['metrics'].get('noise_count', 0),
                # Hierarchical
                hierarchical_silhouette=results['hierarchical']['metrics']['silhouette_score'],
                hierarchical_zas=results['hierarchical']['metrics']['zoning_alignment_score'],
                hierarchical_calinski=results['hierarchical']['metrics']['calinski_harabasz_score'],
                hierarchical_davies=results['hierarchical']['metrics']['davies_bouldin_score'],
                hierarchical_execution_time=results['hierarchical']['metrics']['execution_time'],
                hierarchical_cluster_count=results['hierarchical']['metrics']['cluster_count'],
            )
            
            self.stdout.write(self.style.SUCCESS('\n=== Comparison Results ===\n'))
            
            # Display table
            for row in comparison_data['comparison_table']:
                self.stdout.write(f"\n{row['algorithm']}:")
                self.stdout.write(f"  Silhouette Score: {row['silhouette_score']:.4f}")
                self.stdout.write(f"  Zoning Alignment Score: {row['zoning_alignment_score']:.4f}")
                self.stdout.write(f"  Execution Time: {row['execution_time']:.4f}s")
                self.stdout.write(f"  Cluster Count: {row['cluster_count']}")
            
            self.stdout.write(self.style.SUCCESS(f"\n\nBest Algorithm: {comparison_data['best_algorithm']}"))
            self.stdout.write(self.style.SUCCESS(f"\nComparison saved to database (ID: {comparison.id})"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            raise

