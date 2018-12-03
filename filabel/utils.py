

def parse_labels(cfg):
    """
    Parse labels of given label config file with ConfigParser to dictionary,
    where label is the key and value is a list of patterns with corresponding value.

    :param dict[str,str] cfg: ConfigParser dictinary with loaded configuration of labels
    :return: Parsed dictinary with label as a key and value as a list of corresponding value
    :rtype: dict[str, list[str]]
    """
    return {
        label: list(filter(None, cfg['labels'][label].splitlines()))
        for label in cfg['labels']
    }
