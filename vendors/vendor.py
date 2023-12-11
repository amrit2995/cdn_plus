from abc import ABC, abstractmethod

class VendorInterface(ABC):

    @abstractmethod
    def create_distribution(self):
        pass
    
    @abstractmethod
    def get_distributionId_by_domain(self, domain_name=None):
        pass
    
    @abstractmethod
    def fetch_all_distributions(self):
        pass
    
    @abstractmethod
    def fetch_distribution_details_by_domain(self):
        pass
    
    @abstractmethod
    def enable_distribution_by_domain(self):
        pass
    
    @abstractmethod
    def disable_distribution_by_domain(self):
        pass

    @abstractmethod
    def delete_distribution_by_domain(self):
        pass
    
    @abstractmethod
    def update_distribution_by_domain(self):
        pass


