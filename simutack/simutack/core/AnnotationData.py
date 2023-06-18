#!/usr/bin/python
# -*- coding: utf-8 -*-

# Imports

class AnnotationData:
    """
    """

    def __init__(self, enabled: bool = False, type: str = '') -> None:
        self.attackEnabled = enabled
        self.attackType = type

    # def __copy__(self):
    #     cls = self.__class__
    #     result = cls.__new__(cls)
    #     result.__dict__.update(self.__dict__)
    #     return result

    def isAttackEnabled(self) -> bool:
        return self.attackEnabled

    def getAttackType(self) -> str:
        return self.attackType
